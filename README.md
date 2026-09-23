# Cross Points and Markers Influence Analysis (CPM-IA)

**Component:** CPM-IA — part of the DMA Screening software system
**SR&TS Reference:** `#L001-U015-P26.0127 Rev 00.01` — 23 September 2026
**Regulatory Framework:** ISO 13485:2016 · EU MDR 2017/745 · IEC 62304 · ISO 14971

> This software is a **Class I medical device software component** under EU MDR 2017/745.
> It supports bioelectrical surface current acquisition (non-invasive).
> All outputs are **for investigational and research use only** — not for diagnostic purposes.

---

## Overview

CPM-IA receives a raw-percentage-variation dataset from the upstream *Raw Variation Computation* component and performs a fully autonomous cross-marker influence analysis. For each (visit, anatomical point) pair the pipeline:

1. Reconstructs the per-visit ordered marker measurement sequence (order of first appearance — immutable for the run).
2. Detects **all positive anchors** — all markers whose raw percentage variation is `>=` the configured threshold.
3. Determines an **adaptive descent window** for each anchor, bounded by a rise-tolerance epsilon, by the next positive marker, or by a maximum length N_max.
4. Computes descent quantitative descriptors per anchor: OLS slope, depth, length, mean per-step decrease, pre/post variance.
5. Aggregates results at two granularities: per-(visit, point, anchor) and per-point across all visits.
6. Compiles an automated **PDF run report** with dataset statistics, data quality summary, algorithm description, and per-point results tables.

All execution parameters are read from an external XML configuration file. No processing parameter is hard-coded in the source.

---

## Requirements

| Dependency | Version tested | Notes |
|------------|---------------|-------|
| Python | 3.9+ | Standard library only for core logic |
| pandas | 2.3.3 | DataFrame operations |
| numpy | 2.0.2 | Numerical utilities |
| openpyxl | 3.1.5 | Excel file reading (ExcelSource) |
| pytest | 8.4.2 | Test suite |
| pdflatex | TeX Live 2023+ | Report compilation (must be on PATH) |

Install Python dependencies:

```bash
pip install pandas numpy openpyxl pytest
```

Install TeX Live (macOS with Homebrew):

```bash
brew install --cask mactex-no-gui
```

Install TeX Live (Debian/Ubuntu):

```bash
apt-get install texlive-latex-extra
```

---

## Project Structure

```
.
├── data/
│   ├── config/
│   │   └── cpm_ia_config.xml          # Runtime configuration (edit this to change parameters)
│   ├── input/                          # Input data — one subdirectory per visit (Excel) or single CSV
│   │   ├── AF_#2026m03d03-AF_FreeProtocol/
│   │   └── TP0010_player0010-test_Tennis/
│   ├── output/                         # Pipeline writes CSV and PDF outputs here
│   └── templates/
│       └── cpm_ia_report.tex.template # LaTeX report template
├── src/
│   ├── config_loader.py               # M01 — XML config loading and validation
│   ├── data_ingestion.py              # M02 — Flexible ingestion (CSV/Excel/DB stub) + data quality
│   ├── marker_sequence.py             # M03 — Per-visit marker order and sequence building
│   ├── trigger_detection.py           # M04 — All-positive anchor detection (>= threshold)
│   ├── positive_census.py             # M05 — Positive-point census
│   ├── descent_window.py              # M06 — Adaptive descent window per anchor
│   ├── descent_slope.py               # M07 — OLS slope per anchor
│   ├── descent_descriptors.py         # M08 — Descent depth, length, mean per-step decrease per anchor
│   ├── variance_indicator.py          # M09 — Pre/post variance per anchor
│   ├── output_consolidation.py        # M10 — Tidy CSV output (per anchor granularity)
│   ├── report_generator.py            # M11 — Automated PDF report compilation
│   └── main.py                        # Pipeline orchestrator (CLI entry point)
├── tests/
│   ├── test_config_loader.py          # 21 tests
│   ├── test_data_ingestion.py         # 17 tests
│   ├── test_marker_sequence.py        # 17 tests
│   ├── test_trigger_detection.py      # 19 tests
│   ├── test_positive_census.py        # 13 tests
│   ├── test_descent_window.py         # 23 tests
│   ├── test_descent_slope.py          # 18 tests
│   ├── test_descent_descriptors.py    # 15 tests
│   ├── test_variance_indicator.py     # 22 tests
│   ├── test_output_consolidation.py   # 25 tests
│   ├── test_main.py                   # 15 tests
│   └── test_report_generator.py       # 33 tests  (238 total)
└── TechDoc/                            # SR&TS and GR documents
```

---

## Configuration

All parameters are defined in `data/config/cpm_ia_config.xml`. Edit this file to change runtime behaviour — never modify source files to adjust parameters.

```xml
<cpm_ia_config>
  <input>
    <type>excel</type>            <!-- csv | excel | db -->
    <csv>
      <path>data/input/all_visits_percentage_variation_cleaned.csv</path>
    </csv>
    <excel>
      <file>
        <path>data/input/AF_.../file_percentage_variation.xlsx</path>
        <visit_id>AF_#2026m03d03-AF_FreeProtocol</visit_id>
        <visit_date>2026-03-03</visit_date>
      </file>
    </excel>
    <db>
      <dsn_env>CPM_IA_PG_DSN</dsn_env>  <!-- connection string via env var, never in plaintext -->
      <query></query>
    </db>
  </input>

  <output_path>data/output</output_path>
  <output_label_detail>cpm_ia_detail</output_label_detail>
  <output_label_aggregated>cpm_ia_aggregated</output_label_aggregated>

  <threshold_pct>300.0</threshold_pct>            <!-- REQUIRED — positive if value >= threshold -->
  <rise_tolerance_epsilon>1.0</rise_tolerance_epsilon>
  <n_max>1000</n_max>

  <data_quality>
    <drop_invalid_points>true</drop_invalid_points>
  </data_quality>
</cpm_ia_config>
```

| Parameter | Current value | Description |
|-----------|--------------|-------------|
| `threshold_pct` | `300.0` | **Required.** A marker is a positive anchor when its percentage variation is `>=` this value. |
| `rise_tolerance_epsilon` | `1.0` | Max consecutive increase still considered non-rising. A rise strictly exceeding ε closes the descent window. To be tuned. |
| `n_max` | `1000` | Hard cap on descent window length per anchor. To be tuned. |
| `drop_invalid_points` | `true` | If `true`, rows with anatomically invalid point names are dropped and logged. If `false`, only a WARNING is emitted. |

**Backward compatibility:** if the `<input>` block is absent, a legacy `<input_path>` element is accepted and treated as a CSV source.

---

## Input Data Format

The component supports three input source types (selected via `<input><type>`):

| Type | Description |
|------|-------------|
| `csv` | Long-format UTF-8 CSV with the required columns listed below. |
| `excel` | Wide-format Excel file(s): markers on rows, anatomical points on columns. Each file is declared with `<path>`, `<visit_id>`, and `<visit_date>` in the config. |
| `db` | Postgres stub (not yet configured — raises a controlled error until DSN is provided). |

Required columns in the long format (produced by all sources):

| Column | Type | Description |
|--------|------|-------------|
| `visit_id` | string | Unique identifier for the visit |
| `marker` | string | Identifier of the measurement marker |
| `point` | string | Identifier of the anatomical point |
| `percentage_variation` | float64 | Raw percentage variation value |
| `visit_date` | string | Visit date (kept as-is, no datetime parsing) |

Valid anatomical point names must match one of:
- New format (4 components): `[LR][HF] - N - type - OrganName` (e.g. `LH - 2 - i - colon`)
- Short format (3 components): `[LR][HF] - N - type` (e.g. `LH - 3 - c`) — 4th component optional
- Legacy format: `Name [N]` (e.g. `SomeName [3]`)

Points not matching any pattern are flagged as invalid and dropped or warned depending on `<drop_invalid_points>`.

---

## Running the Pipeline

All commands are run from the project root.

### Single visit (e.g. AF visit)

```bash
python3 -m src.main data/config/cpm_ia_config_AF.xml
```

### Batch of visits (e.g. ALL_VISITS — 997 visits)

```bash
python3 -m src.main data/config/cpm_ia_config_all_visits.xml
```

In batch mode (Excel input with multiple `<file>` entries), the pipeline runs once per visit and writes each visit's outputs to `<output_path>/<visit_id>/`. Per-visit errors (empty dataset, duplicate markers) are logged as `WARNING` and skipped — the remaining visits continue.

### Generic

```bash
python3 -m src.main <path/to/config.xml>
```

The pipeline exits with code `0` on success and `1` on any unrecoverable error. All stages log to stdout in ISO-8601 timestamped format.

> **G-10 guard:** The pipeline will not overwrite existing output files. If a previous run's outputs are present, delete the relevant folder before re-running:
> ```bash
> rm -rf data/output/AF_#2026m03d03-AF_FreeProtocol
> python3 -m src.main data/config/cpm_ia_config_AF.xml
> ```

---

## Output Files

All outputs are written to the directory specified in `<output_path>`.

| File | Description |
|------|-------------|
| `cpm_ia_detail.csv` | One row per (visit, anatomical point, anchor). Series with no positives have one row with `no_cross_marker_effect=True` and anchor fields set to None. Columns include: `anchor_rank`, `anchor_marker`, `anchor_value`, `anchor_index`, `positives_count`, `window_close_reason`, descent metrics, and variance indicators. |
| `cpm_ia_aggregated.csv` | One row per anatomical point. Columns: `total_visit_count`, `positive_visit_count`, `positive_prevalence`, `median_positives_count`, and median descent metrics across all anchors of that point. |
| `cpm_ia_report.pdf` | Automated PDF run report. Contains run metadata, data quality summary, dataset overview, algorithm description, and per-point results tables. |
| `cpm_ia_report.tex` | Filled LaTeX source for the PDF (preserved on compilation failure). |

---

## Algorithm Summary

The pipeline executes eleven modules in strict sequential order:

```
M01 config_loader  →  M02 data_ingestion  →  M03 marker_sequence
→  M04 trigger_detection  →  M05 positive_census  →  M06 descent_window
→  M07 descent_slope  →  M08 descent_descriptors  →  M09 variance_indicator
→  M10 output_consolidation  →  M11 report_generator
```

**Key design invariants:**
- Marker order is derived **once per visit** from the order of first appearance of each marker in that visit's rows. This order is immutable for the entire run.
- **All markers** meeting `value >= threshold_pct` are collected as anchors (in sequence order) for each (visit, point). The anchors list is immutable once assigned.
- Each anchor produces an independent descent window, closed by the first of: a rise > ε, the next positive marker, the n_max cap, or the sequence end. The closure reason is recorded in `window_close_reason`.
- The OLS slope is computed with the closed-form formula; no third-party regression library is used.
- Series with no threshold-meeting marker are explicitly flagged (`no_cross_marker_effect = True`) and always included in outputs (one row per series).
- The unique key for the detail output is `(visit_id, point, anchor_marker)` (G-09).

---

## Running the Tests

```bash
python3 -m pytest tests/ -v
```

Expected result: **238 tests passed**.

To run a single module's test file:

```bash
python3 -m pytest tests/test_trigger_detection.py -v
```

---

## Regulatory & Traceability Notes

- Every source file carries a `# LINKED-TO: [REQ-CPM-IA-P26.XXXX]` traceability anchor.
- The SR&TS document (`TechDoc/#L001-U015-P26.0127`) defines all functional requirements referenced in the test IDs (e.g., `TC-07-005` traces to Module 07 test 5).
- This component was developed under SOP `#L001-U015-P26.0141` (Agentic Development WorkFlow). The AI generation record is maintained in `CLAUDE.md`.
- No output of this software constitutes a medical diagnosis or clinical recommendation.

---

## Author

Ilaria Rocco — Math Biology R&D
`Ilaria.Rocco@mathbiology.tech`
