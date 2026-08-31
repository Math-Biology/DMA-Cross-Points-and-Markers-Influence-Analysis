# Cross Points and Markers Influence Analysis (CPM-IA)

**Component:** CPM-IA — part of the DMA Screening software system
**SR&TS Reference:** `#L001-U015-P26.0127 Rev 00.00` — 26 August 2026
**Regulatory Framework:** ISO 13485:2016 · EU MDR 2017/745 · IEC 62304 · ISO 14971

> This software is a **Class I medical device software component** under EU MDR 2017/745.
> It supports bioelectrical surface current acquisition (non-invasive).
> All outputs are **for investigational and research use only** — not for diagnostic purposes.

---

## Overview

CPM-IA receives a raw-percentage-variation dataset from the upstream *Raw Variation Computation* component and performs a fully autonomous cross-marker influence analysis. For each (visit, anatomical point) pair the pipeline:

1. Reconstructs the per-visit ordered marker measurement sequence (order of first appearance — immutable for the run).
2. Detects the **first positive anchor** — the first marker whose raw percentage variation exceeds the configured threshold.
3. Determines an **adaptive descent window** from the anchor, bounded by a rise-tolerance epsilon and a maximum length N_max.
4. Computes descent quantitative descriptors: OLS slope, depth, length, mean per-step decrease, pre/post variance.
5. Aggregates results at two granularities: per-(visit, point) and per-point across all visits.
6. Compiles an automated **PDF run report** with dataset statistics, algorithm description, and per-point results tables.

All execution parameters are read from an external XML configuration file. No processing parameter is hard-coded in the source.

---

## Requirements

| Dependency | Version tested | Notes |
|------------|---------------|-------|
| Python | 3.9+ | Standard library only for core logic |
| pandas | 2.3.3 | DataFrame operations |
| numpy | 2.0.2 | Numerical utilities |
| pytest | 8.4.2 | Test suite |
| pdflatex | TeX Live 2023+ | Report compilation (must be on PATH) |

Install Python dependencies:

```bash
pip install pandas numpy pytest
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
│   ├── input/                          # Place input CSV here (path set in config)
│   ├── mock/
│   │   └── raw_variation_mock.csv     # Minimal mock dataset used by integration tests
│   ├── output/                         # Pipeline writes CSV and PDF outputs here
│   └── templates/
│       └── cpm_ia_report.tex.template # LaTeX report template
├── src/
│   ├── config_loader.py               # M01 — XML config loading and validation
│   ├── data_ingestion.py              # M02 — CSV ingestion and schema validation
│   ├── marker_sequence.py             # M03 — Per-visit marker order and sequence building
│   ├── trigger_detection.py           # M04 — First-positive anchor detection
│   ├── positive_census.py             # M05 — Positive-point census
│   ├── descent_window.py              # M06 — Adaptive descent window extraction
│   ├── descent_slope.py               # M07 — OLS slope estimation
│   ├── descent_descriptors.py         # M08 — Descent depth, length, mean per-step decrease
│   ├── variance_indicator.py          # M09 — Pre/post variance and variance ratio
│   ├── output_consolidation.py        # M10 — Tidy CSV output assembly and writing
│   ├── report_generator.py            # M11 — Automated PDF report compilation
│   └── main.py                        # Pipeline orchestrator (CLI entry point)
├── tests/
│   ├── test_config_loader.py          # 13 tests
│   ├── test_data_ingestion.py         # 16 tests
│   ├── test_marker_sequence.py        # 17 tests
│   ├── test_trigger_detection.py      # 15 tests
│   ├── test_positive_census.py        # 10 tests
│   ├── test_descent_window.py         # 21 tests
│   ├── test_descent_slope.py          # 17 tests
│   ├── test_descent_descriptors.py    # 20 tests
│   ├── test_variance_indicator.py     # 26 tests
│   ├── test_output_consolidation.py   # 25 tests
│   ├── test_main.py                   # 13 tests
│   └── test_report_generator.py       # 48 tests  (241 total)
└── TechDoc/                            # SR&TS and GR documents
```

---

## Configuration

All parameters are defined in `data/config/cpm_ia_config.xml`. Edit this file to change runtime behaviour — never modify source files to adjust parameters.

```xml
<cpm_ia_config>
    <!-- I/O -->
    <input_path>data/input/all_visits_percentage_variation_cleaned.csv</input_path>
    <output_path>data/output</output_path>
    <output_label_detail>cpm_ia_detail</output_label_detail>
    <output_label_aggregated>cpm_ia_aggregated</output_label_aggregated>

    <!-- Analysis parameters -->
    <threshold_pct>300.0</threshold_pct>          <!-- Positive-detection threshold (%) -->
    <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    <n_max>10</n_max>                              <!-- Maximum descent window length -->
</cpm_ia_config>
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `threshold_pct` | `300.0` | Raw percentage variation that must be **exceeded** (strictly `>`) for a marker to be flagged as a first positive. |
| `rise_tolerance_epsilon` | `5.0` | Tolerance (same unit as the variation values) used to close the descent window when a rise is detected. |
| `n_max` | `10` | Maximum number of steps in the descent window. Windows that reach this cap are flagged as truncated. |

---

## Input Data Format

Long-format UTF-8 CSV with the following required columns:

| Column | Type | Description |
|--------|------|-------------|
| `visit_id` | string | Unique identifier for the visit |
| `marker_id` | string | Identifier of the measurement marker |
| `point_id` | string | Identifier of the anatomical point |
| `raw_pct_variation` | float64 | Raw percentage variation value |
| `visit_date` | string | Visit date (kept as-is, no datetime parsing) |

Additional columns are carried forward as visit metadata in the detail output.

The file path is specified in `cpm_ia_config.xml` under `<input_path>`.

---

## Running the Pipeline

```bash
python -m src.main data/config/cpm_ia_config.xml
```

The pipeline exits with code `0` on success and `1` on any error. All stages log to stdout in ISO-8601 timestamped format.

> **G-10 guard:** The pipeline will not overwrite existing output files. Delete or move previous outputs before re-running:
> ```bash
> rm data/output/cpm_ia_*
> ```

---

## Output Files

All outputs are written to the directory specified in `<output_path>`.

| File | Description |
|------|-------------|
| `cpm_ia_detail.csv` | One row per (visit, anatomical point). Carries the anchor marker, descent metrics (slope, depth, length, mean per-step decrease), and variance indicators (before, after, ratio). |
| `cpm_ia_aggregated.csv` | One row per anatomical point. Carries visit counts, positive prevalence, and median descent metrics across all visits. |
| `cpm_ia_report.pdf` | Automated PDF run report. Contains run metadata, dataset overview, algorithm description, and three per-point results tables. |
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
- The anchor (first positive marker) per (visit, point) series is set at detection time and cannot be reassigned during the run.
- The OLS slope is computed with the closed-form formula; no third-party regression library is used.
- Series with no threshold-exceeding marker are explicitly flagged (`no_cross_marker_effect = True`) and always included in outputs.

---

## Running the Tests

```bash
python -m pytest tests/ -v
```

Expected result: **241 tests passed**.

To run a single module's test file:

```bash
python -m pytest tests/test_report_generator.py -v
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
