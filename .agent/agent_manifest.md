# Agent Manifest — CPM-IA Component
**Component:** Cross Points and Markers Influence Analysis
**Short Code:** CPM-IA
**SR&TS Document:** `#L001-U015-P26.0127 Rev 00.00` — 26 August 2026
**Regulatory Framework:** ISO 13485:2016 · EU MDR 2017/745 · IEC 62304 · ISO 14971
**Device Class:** Class I (DMA Screening — non-invasive bioelectrical acquisition)
**Author (SR&TS):** Ilaria Rocco [IR]

---

## 1. Component Purpose

The CPM-IA component receives the consolidated raw-percentage-variation dataset produced by the upstream **Raw Variation Computation** component and performs a fully autonomous cross-marker influence analysis. For each (visit, anatomical point) pair it:

1. Reconstructs the ordered marker measurement sequence.
2. Detects the **first positive** — the first marker whose raw percentage variation exceeds a configurable threshold (default 300 %).
3. Determines an **adaptive descent window** starting from that anchor.
4. Computes quantitative descriptors of the descent (slope, depth, length, mean per-step decrease, pre/post variance).
5. Aggregates and exports tidy outputs at two granularities: per-(visit, point) and per-point across visits.
6. Compiles an automated PDF run report (Module 11) summarising dataset statistics, algorithm description, and per-point results.

All execution parameters are loaded from an external XML configuration file; no processing parameter is hard-coded.

---

## 2. Regulatory & Safety Guardrails

| # | Guardrail | Origin |
|---|-----------|--------|
| G-01 | All parameters (threshold, epsilon, N_max, paths, labels) **must** be read from the XML config; hard-coding any processing parameter is forbidden. | REQ-CPM-IA-P26.0001 |
| G-02 | A missing or malformed configuration file **must** cause a controlled failure (no partial run). | REQ-CPM-IA-P26.0001 |
| G-03 | Input field validation **must** be performed before any computation begins; missing required columns abort the run. | REQ-CPM-IA-P26.0002 |
| G-04 | Marker ordering **must** be determined deterministically from order-of-first-appearance in the dataset; no random or locale-dependent sorting. | REQ-CPM-IA-P26.0003 |
| G-05 | Only the **first** threshold-exceeding marker per series serves as anchor; subsequent exceedances do not redefine the anchor. | REQ-CPM-IA-P26.0004 |
| G-06 | Series with no threshold-exceeding marker **must** be explicitly flagged (no_cross_marker_effect = True) and included in outputs. | REQ-CPM-IA-P26.0004 |
| G-07 | Descent window **must** be truncated at N_max points regardless of actual descent length. | REQ-CPM-IA-P26.0006 |
| G-08 | Slope estimation **must** use standard OLS least-squares linear regression; no alternative estimators. | REQ-CPM-IA-P26.0007 |
| G-09 | All outputs **must** be in long (tidy) format, uniquely identified by grouping keys + visit metadata. | REQ-CPM-IA-P26.0010 |
| G-10 | No output file may overwrite an existing file without explicit path separation (output suffix from config). | REQ-CPM-IA-P26.0001 |

---

## 3. Module Tracking Log

| # | Module File | SR Linked | Status |
|---|-------------|-----------|--------|
| 01 | `src/config_loader.py` | REQ-CPM-IA-P26.0001 | Complete |
| 02 | `src/data_ingestion.py` | REQ-CPM-IA-P26.0002 | Complete |
| 03 | `src/marker_sequence.py` | REQ-CPM-IA-P26.0003 | Complete |
| 04 | `src/trigger_detection.py` | REQ-CPM-IA-P26.0004 | Complete |
| 05 | `src/positive_census.py` | REQ-CPM-IA-P26.0005 | Complete |
| 06 | `src/descent_window.py` | REQ-CPM-IA-P26.0006 | Complete |
| 07 | `src/descent_slope.py` | REQ-CPM-IA-P26.0007 | Complete |
| 08 | `src/descent_descriptors.py` | REQ-CPM-IA-P26.0008 | Complete |
| 09 | `src/variance_indicator.py` | REQ-CPM-IA-P26.0009 | Complete |
| 10 | `src/output_consolidation.py` | REQ-CPM-IA-P26.0010 | Complete |
| 11 | `src/report_generator.py` | REQ-CPM-IA-P26.0011 | Complete |
| — | `src/main.py` | All (pipeline orchestrator) | Complete |

Status legend: Not Started / In Progress / Complete / Blocked

---

## 4. Current Run Summary

**Last updated:** 2026-08-31
**Phase:** SOP Step 4 — Modular Development
**Active module:** — ALL MODULES COMPLETE (01–11)
**Blocking issues:** None
**Next action:** SOP Step 5 — Formal Verification (update SR&TS, independent QA)

### Session log — 2026-08-31 Documentation alignment

- `CLAUDE.md` updated: immutability criterion now reads "Marker order derived once **per visit** at ingestion (order of first appearance within each visit's rows) — immutable for the entire run."
- `.agent/modules/03_marker_sequence.md` rewritten: reflects per-visit `PerVisitMarkerOrders` output, 17/17 tests, TC-03-001 through TC-03-009.
- `.agent/modules/04_trigger_detection.md` rewritten: input changed from `marker_order: list[str]` to `marker_orders: PerVisitMarkerOrders`; step 1a now reads `visit_marker_order = marker_orders[visit]`.
- `.agent/modules/09_variance_indicator.md` updated: `variance_ratio` field added to `VarianceIndicator` table; behaviour spec step 2e documented; TC-09-010 added to test table; status 26/26.
- `.agent/modules/10_output_consolidation.md` updated: `variance_ratio | Module 09` row added to Output 1 detail table; status date updated.
- `agent_manifest.md` updated: M11 row fixed to `src/report_generator.py | REQ-CPM-IA-P26.0011`; `src/main.py` listed as pipeline orchestrator; 2026-08-31 session logs added; test counts updated.
- `.agent/modules/11_report_generator.md` created: full spec for M11 (interface, behaviour, placeholders, TC-11-001–018, 48 tests).
- Cumulative: 241/241 tests passing.

### Session log — 2026-08-31 Report enhancements

- Cover page: removed MDR Class and Operator rows. Now shows Component ID, SR&TS Reference, Run date, Run time only — all read from `CpmIaConfig` and `run_dt`.
- Section 3 (Algorithm Description) added: covers Input Data, Configuration Parameters (threshold_pct, rise_tolerance_epsilon, n_max from config), Processing Steps M03–M10 with OLS slope formula in display math, Output Artefacts. All numeric values in this section are template placeholders filled from config at runtime.
- Section 4.1 (Per-Point Visit Counts): column spec fixed from `l` to `p{5cm}` to prevent right-margin overflow.
- Section 4.2 renamed "Most Frequent Trigger Markers by Anatomical Point": filters to `anchor_pct >= 3.5 %` of positive visits per point (6,058 raw rows → 286 rows covering all 62 points). Column spec changed to `p{3.5cm}p{7.5cm}rr` with `\footnotesize` and longtable line-breaking. Threshold value (`3.5`) is a template placeholder `__ANCHOR_TABLE_THRESHOLD__`.
- Section 4.3 (Descent Metrics): column spec fixed from `l` to `p{4.5cm}rrrr`.
- All section descriptions (how to read tables, metric definitions, calculation methods) added in English.
- `TRUNCATED_COUNT` and `TRUNCATED_RATE` placeholders now used in Dataset Overview table (Section 2).

### Session log — 2026-08-31 M11 report_generator

- `src/report_generator.py` implemented: `ReportError`, `_escape()`, `_fmt()`, `_fill_template()`, `_build_values()`, `_run_pdflatex()`, `generate_report()`.
- Template: `data/templates/cpm_ia_report.tex.template` — multi-section LaTeX document (longtable, geometry, booktabs, amsmath). Three per-point result tables, algorithm description section, dataset overview.
- `generate_report()` called from `src/main.py` as the final pipeline step (M11). `run_dt = datetime.utcnow()` is captured at pipeline start and passed through.
- G-10 enforced: raises `ReportError` if PDF already exists at target path before compilation.
- Two pdflatex passes required for correct TOC page numbers.
- Auxiliary files (`.aux`, `.log`, `.out`, `.toc`) removed after successful compilation.
- `.tex` source preserved on pdflatex failure to enable post-mortem inspection.
- 48/48 unit tests pass (`tests/test_report_generator.py`). Cumulative: 241/241 passing.

### Session log — 2026-08-31 C1 control character fix

- 35 marker names in real data contain C1 control characters (U+0080–U+009F) from double-encoded UTF-8 artefacts. These are not valid in pdflatex even with `utf8` inputenc.
- Fix: added `_C1_CTRL_DEL = str.maketrans("", "", "".join(chr(i) for i in range(0x80, 0xA0)))` and applied it in `_escape()` before `_LATEX_TRANS`: `str(value).translate(_C1_CTRL_DEL).translate(_LATEX_TRANS)`.
- Stripping is correct behaviour; visual garbling (e.g., "ãâ" sequences in marker names) is a source data quality issue, not a LaTeX issue.

### Session log — 2026-08-31 variance_ratio addition

- `VarianceIndicator` dataclass extended with third field `variance_ratio: Optional[float]`.
- Computed as `variance_after / variance_before` when both are defined and `variance_before > 0`; `None` otherwise.
- `src/output_consolidation.py`: `_ANALYTICAL_COLS` updated to include `"variance_ratio"` as the last entry; detail CSV now carries this column.
- 6 new unit tests added to `tests/test_variance_indicator.py` (TC-09-010). Prior: 20/20. Updated: 26/26.

### Session log — 2026-08-31 Per-visit marker order fix

- **Architecture change:** Marker ordering is now per-visit, not global. `PerVisitMarkerOrders = Dict[str, List[str]]` replaces the single `List[str]` used previously.
- `src/marker_sequence.py`: `build_sequences(df)` now returns `(per_visit_orders: PerVisitMarkerOrders, sequences: Sequences)`. Order-of-first-appearance is derived independently for each visit from its own rows.
- `src/trigger_detection.py`: `detect_triggers(sequences, marker_orders: PerVisitMarkerOrders, threshold_pct)` — step 1a now retrieves `visit_marker_order = marker_orders[visit]` per series.
- `src/main.py`: updated call sites for `build_sequences` (unpack two-tuple) and `detect_triggers` (pass `marker_orders`); `generate_report` call added as M11.
- 4 new unit tests added to `tests/test_marker_sequence.py`. Prior: 13/13. Updated: 17/17.
- Cumulative prior to this session: 182/182.

---

### Session log — 2026-08-27 Module 11

- `src/main.py` implemented: `run_pipeline()` (callable, returns `(df_detail, df_agg)`), `main()` (CLI entry, wraps run_pipeline, sys.exit 0/1), `_configure_logging()`.
- No `11_main.md` spec file existed; plan derived from agent_manifest.md execution order and all prior module interfaces. Architecture confirmed by [IR] with "approved".
- Pipeline order: M01 load_config → M02 load_data → M03 build_sequences → M04 detect_triggers → M05 compute_census → M06 determine_descent_windows → M07 compute_slopes → M08 compute_descriptors → M09 compute_variance_indicators → M10 consolidate_outputs.
- `run_pipeline` is the testable unit; `main()` wraps it with sys.exit for CLI use. Tests call `run_pipeline` directly to avoid sys.exit interference.
- Integration tests use `data/mock/raw_variation_mock.csv` (all 4 (visit,point) pairs exceed threshold_pct=300) + a temp config XML redirecting output to `tmp_path`.
- Test fix: `pytest.approx(1.0)` with Series `.all()` is not element-wise compatible; replaced with explicit Python `all(abs(v-1.0) < 1e-9 for v in ...)`.
- 13/13 unit+integration tests pass (`tests/test_main.py`). Cumulative: 182/182 passing.

### Session log — 2026-08-27 Module 10

- `src/output_consolidation.py` implemented: `OutputError`, `consolidate_outputs()`, private helpers `_build_detail()`, `_build_aggregation()`, `_cross_check_census()`, `_write_outputs()`.
- HALT-1A resolved by [IR]: `point_id` renamed to `"point"` in output CSV.
- HALT-1B resolved by [IR]: all `df_raw` columns except `marker_id` and `raw_pct_variation` carry forward as visit metadata (programmatically derived — no hard-coded column list).
- HALT-2 resolved by [IR]: `census` is used for internal cross-validation only (WARNING log, no CSV output). Census fields do not appear in output tables.
- G-09 enforced: uniqueness check after metadata join — `OutputError` if any `(visit_id, point_id)` pair duplicated (TC-10-005).
- G-10 enforced: `OutputError` raised if detail or aggregation file already exists before write (TC-10-003).
- Output path auto-created with WARNING log if it does not exist (TC-10-006).
- Aggregation medians computed over positive-visit rows only (`no_cross_marker_effect=False`); pandas `.median()` skips NaN naturally for sparse slope/descriptor fields.
- `census` cross-validation emits WARNING if `total_point_count` or `positive_point_count` diverge from aggregation counts.
- 25/25 unit tests pass (`tests/test_output_consolidation.py`). Cumulative: 169/169 passing.

### Session log — 2026-08-27 Module 09

- `src/variance_indicator.py` implemented: `VarianceIndicator` (frozen dataclass), `compute_variance_indicators()`.
- No custom exception class: the spec defines no raise conditions; all edge cases resolve to `None` fields.
- Before segment: `sequence[0:anchor_index]` (excludes anchor), NaN stripped. `variance_before=None` when < 2 clean values remain (TC-09-002, TC-09-005, TC-09-007).
- After segment: `descent_window_values` (includes anchor at position 0), NaN stripped defensively. `variance_after=None` when < 2 clean values (TC-09-003).
- Variance formula: `statistics.variance` (Python stdlib, `ddof=1` sample variance by default) per REQ-CPM-IA-P26.0009 spec point 3.
- TC-09-001 cross-validates against `statistics.variance` directly as independent reference.
- 20/20 unit tests pass (`tests/test_variance_indicator.py`). Cumulative: 144/144 passing.

### Session log — 2026-08-27 Module 08

- `src/descent_descriptors.py` implemented: `DescriptorError`, `DescentDescriptor` (frozen dataclass), `compute_descriptors()`.
- Three mandatory descriptors per REQ-CPM-IA-P26.0008: `descent_depth`, `descent_length`, `mean_per_step_decrease`.
- `descent_depth = anchor_value - min(window_values)` — uses global minimum, not last value; these differ when the window contains epsilon-bounded rises (TC-08-006 tests this explicitly).
- `mean_per_step_decrease = depth / (length-1)` for length > 1; `0.0` for length == 1 (TC-08-002).
- Anchor value sourced from `trigger_results.first_positive_value`; `DescriptorError` raised if None with non-None window (TC-08-005).
- NaN guard is defensive (Module 06 already strips NaN from window_values); tested in TC-08-004.
- Output type: frozen dataclass (consistent with all prior modules; spec table notation describes fields, not a literal plain dict).
- 20/20 unit tests pass (`tests/test_descent_descriptors.py`). Cumulative: 124/124 passing.

### Session log — 2026-08-27 Module 07

- `src/descent_slope.py` implemented: `SlopeError`, `_ols_slope()`, `compute_slopes()`.
- Closed-form OLS formula used directly (from REQ-CPM-IA-P26.0007): slope = (n·Σ(i·yᵢ) − Σi·Σyᵢ) / (n·Σi² − (Σi)²).
- G-08 enforced: standard OLS only; no alternative estimators.
- `SlopeError` raised if any NaN present in window (should not occur with valid Module 06 output).
- `None` + WARNING log returned for single-point windows (L=1; regression undefined).
- Tests cross-validate against `numpy.polyfit` as independent OLS reference (TC-07-005).
- 17/17 unit tests pass (`tests/test_descent_slope.py`). Cumulative: 104/104 passing.

### Session log — 2026-08-27 Module 06

- `src/descent_window.py` implemented: `DescentError`, `DescentWindow` (frozen dataclass), `determine_descent_windows()`.
- Decision A confirmed by [IR]: NaN values after anchor are bridged — `prev` retains the last non-NaN value; NaN positions do not consume n_max slots.
- Decision B confirmed by [IR]: `truncated_by_n_max=True` only when the n_max cap fires before a natural close (rise or sequence end). n_max=1 with a non-rising next value → truncated=True.
- Check order in inner loop: (1) NaN skip, (2) rise check, (3) n_max check — rise takes priority over n_max so boundary simultaneity is handled correctly.
- G-07 enforced: hard cap applied regardless of actual descent length.
- 21/21 unit tests pass (`tests/test_descent_window.py`).

### Session log — 2026-08-27 Module 05

- `src/positive_census.py` implemented: `PointCensus` (frozen dataclass), `compute_census()`.
- `sorted()` used intentionally for `positive_points` — spec-mandated for deterministic output. Contrast with G-04 (Module 03) where sorting was forbidden.
- `total_point_count` counts unique anatomical points, not (visit, point) pairs.
- Empty input returns `PointCensus(0, [], 0)` — not an error.
- 10/10 unit tests pass (`tests/test_positive_census.py`).

### Session log — 2026-08-27 Module 04

- `src/trigger_detection.py` implemented: `TriggerError`, `TriggerResult` (frozen dataclass), `detect_triggers()`.
- G-05 enforced via `break` on first exceedance in `for/else` loop pattern.
- G-06 enforced: every (visit, point) key is always written to `trigger_results`, including no-effect series.
- Threshold comparison is strictly `>` (exceeds), not `>=` — value equal to threshold is NOT a positive.
- Explicit `math.isnan()` skip added for clarity; `float('nan') > threshold` also evaluates False but intent must be unambiguous in safety-critical code.
- 15/15 unit tests pass (`tests/test_trigger_detection.py`).

### Session log — 2026-08-27 Module 03

- `src/marker_sequence.py` implemented: `SequenceError`, `build_sequences()`.
- G-04 enforced via `dict.fromkeys(df[COL_MARKER])` — pure Python ordered-dict pattern; `.unique()` and `sorted()` explicitly avoided.
- `groupby(sort=False)` used to preserve group discovery order without implicit alphabetic sorting.
- Duplicate detection uses `duplicated(keep=False)` on the marker column per group; reports first offending DataFrame row index.
- 13/13 unit tests pass (`tests/test_marker_sequence.py`), including TC-03-007 full index-to-marker consistency check.

### Session log — 2026-08-27 Module 02

- `src/data_ingestion.py` implemented: `IngestionError`, column constants, `load_data()`.
- Column names confirmed by [IR]: `visit_id`, `marker_id`, `point_id`, `raw_pct_variation`, `visit_date`.
- `visit_date` kept as string/object — no datetime parsing at ingestion (confirmed by [IR]).
- NaN detection in `raw_pct_variation` uses `pd.to_numeric(errors="coerce").isna()` — catches both coercion failures and pandas-auto-converted "N/A" strings.
- 16/16 unit tests pass (`tests/test_data_ingestion.py`).
- Mock CSV written to `data/mock/raw_variation_mock.csv` (2 visits × 4 markers × 2 points = 16 rows).

### Session log — 2026-08-27 Module 01

- `src/config_loader.py` implemented: `ConfigurationError`, `CpmIaConfig` (frozen dataclass), `load_config()`.
- Design decision confirmed by [IR]: blank/whitespace-only text in a required XML element is treated as absent → raises `ConfigurationError`.
- `int` cast for `n_max` is strict: `"10.0"` is rejected (Python `int()` raises `ValueError` on float-like strings).
- 13/13 unit tests pass (`tests/test_config_loader.py`).
- Mock XML written to `data/config/cpm_ia_config.xml`.
