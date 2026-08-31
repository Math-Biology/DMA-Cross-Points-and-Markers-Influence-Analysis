# Module 11 — Automated PDF Run Report
**File:** `src/report_generator.py`
**SR:** REQ-CPM-IA-P26.0011 — Automated PDF Run Report
**Template:** `data/templates/cpm_ia_report.tex.template`
**Status:** Complete — 2026-08-31 | 48/48 tests pass

---

## Requirement (verbatim)

The component shall automatically generate a PDF run report at the end of each pipeline execution. The report shall contain the run metadata (date, time, configuration parameters), a summary of dataset statistics, a description of the algorithm and its processing steps, and per-point results tables. All numeric values in the report shall be read directly from pipeline outputs and configuration; no value shall be hard-coded in the report template or generator code.

---

## Functional Boundary

This module is invoked as the final step of the pipeline (after Module 10). It receives the consolidated DataFrames and all intermediate pipeline outputs, fills a LaTeX template with computed values, and compiles the result to PDF via two pdflatex passes. On failure the `.tex` source is preserved; auxiliary files (`.aux`, `.log`, `.out`, `.toc`) are removed on success.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `df_detail` | `pd.DataFrame` | Per-(visit, point) detail DataFrame from Module 10. |
| `df_agg` | `pd.DataFrame` | Per-point aggregation DataFrame from Module 10. |
| `trigger_results` | `TriggerResults` | Anchor detection results from Module 04. |
| `census` | `PointCensus` | Positive-point census from Module 05. |
| `descent_windows` | `DescentWindows` | Descent windows from Module 06. |
| `marker_orders` | `PerVisitMarkerOrders` | Per-visit marker detection orders from Module 03. |
| `config` | `CpmIaConfig` | Output paths, label suffixes, and all run parameters. |
| `run_dt` | `datetime` | Pipeline start datetime (UTC), captured in `src/main.py` before M01. |

---

## Outputs

| Artefact | Path | Written when |
|----------|------|-------------|
| `{report_stem}.tex` | `config.output_path` | Always (before compilation attempt) |
| `{report_stem}.pdf` | `config.output_path` | On successful pdflatex compilation |

`report_stem` is derived from `config.output_label_detail` by replacing the `_detail` suffix with `_report` (e.g. `cpm_ia_detail` → `cpm_ia_report`).

---

## Template Placeholders

All values written into the template are strings. Numeric formatting uses `_fmt()` (fixed-point, `---` for None/NaN) or explicit f-string formatting. Path strings and label strings are sanitised with `_escape()`.

| Placeholder | Source | Format |
|-------------|--------|--------|
| `__RUN_DATE__` | `run_dt` | `%Y-%m-%d` |
| `__RUN_TIME__` | `run_dt` | `%H:%M:%S` |
| `__INPUT_PATH__` | `config.input_path` | `_escape(str(...))` |
| `__OUTPUT_PATH__` | `config.output_path` | `_escape(str(...))` |
| `__OUTPUT_LABEL_DETAIL__` | `config.output_label_detail` | `_escape(...)` |
| `__OUTPUT_LABEL_AGGREGATED__` | `config.output_label_aggregated` | `_escape(...)` |
| `__THRESHOLD_PCT__` | `config.threshold_pct` | `:.1f` |
| `__RISE_EPSILON__` | `config.rise_tolerance_epsilon` | `str(...)` |
| `__N_MAX__` | `config.n_max` | `str(...)` |
| `__TOTAL_VISITS__` | `df_detail["visit_id"].nunique()` | `str(...)` |
| `__TOTAL_POINTS__` | `census.total_point_count` | `str(...)` |
| `__TOTAL_MARKERS__` | unique markers across all `marker_orders` | `str(...)` |
| `__TOTAL_SERIES__` | `len(trigger_results)` | `str(...)` |
| `__POSITIVE_SERIES__` | series with `no_cross_marker_effect=False` | `str(...)` |
| `__NO_EFFECT_SERIES__` | `total_series - positive_series` | `str(...)` |
| `__POSITIVE_RATE__` | `positive_series / total_series * 100` | `:.1f` |
| `__NO_EFFECT_RATE__` | `100 - positive_rate` | `:.1f` |
| `__POSITIVE_POINTS__` | `census.positive_point_count` | `str(...)` |
| `__NO_EFFECT_POINTS__` | `total_point_count - positive_points` | `str(...)` |
| `__TOTAL_POINT_COUNT__` | `census.total_point_count` | `str(...)` |
| `__POSITIVE_POINTS_RATE__` | `positive_points / total_point_count * 100` | `:.1f` |
| `__NO_EFFECT_POINTS_RATE__` | `100 - positive_points_rate` | `:.1f` |
| `__TRUNCATED_COUNT__` | windows with `truncated_by_n_max=True` (positive series only) | `str(...)` |
| `__TRUNCATED_RATE__` | `truncated / positive_series * 100` | `:.1f` |
| `__AGG_TABLE_COUNTS__` | rows of the per-point visit counts table | `\n.join(...)` |
| `__AGG_TABLE_MEDIANS__` | rows of the per-point descent medians table | `\n.join(...)` |
| `__ANCHOR_TABLE_ROWS__` | rows of the anchor marker frequency table | `\n.join(...)` |
| `__ANCHOR_TABLE_THRESHOLD__` | filter threshold for anchor table | `"3.5"` (literal) |

---

## Behaviour Specification

1. Verify the LaTeX template file exists at `_TEMPLATE_PATH`; raise `ReportError` if absent.
2. Verify `pdflatex` is on PATH via `shutil.which`; raise `ReportError` if absent.
3. Derive `report_stem` from `config.output_label_detail.removesuffix("_detail") + "_report"`.
4. Raise `ReportError` (G-10) if the target PDF already exists.
5. Create `output_dir` if it does not exist.
6. Call `_build_values()` to compute all placeholder values from pipeline outputs.
7. Fill the template via `_fill_template()` and write the `.tex` file.
8. Execute two pdflatex passes (`_run_pdflatex(tex_path, output_dir)` × 2) for correct TOC page numbers.
9. Remove auxiliary files (`.aux`, `.log`, `.out`, `.toc`) produced by pdflatex.
10. Raise `ReportError` if the PDF is absent after compilation.
11. Return the `Path` of the compiled PDF.

### `_build_values` — anchor table filter

The anchor marker table is filtered to rows where `anchor_pct >= 3.5 %` of positive visits for that point have that anchor marker. This reduces the table from all unique (point, anchor_marker) pairs to the most frequent triggers per point. The threshold value (`3.5`) is written to the template as `__ANCHOR_TABLE_THRESHOLD__`.

### `_escape` — LaTeX sanitisation

All string values derived from data or config paths are passed through `_escape()`, which:
1. Strips C1 control characters (U+0080–U+009F) via `_C1_CTRL_DEL` — these arise from double-encoded UTF-8 marker names and are fatal to pdflatex.
2. Translates LaTeX special characters (`& % $ # _ { } ~ ^ \`) to their safe text-mode equivalents via `_LATEX_TRANS`.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| LaTeX template not found | `ReportError("LaTeX template not found: <path>")` |
| `pdflatex` not on PATH | `ReportError("pdflatex not found on PATH ...")` |
| PDF already exists (G-10) | `ReportError("Report PDF already exists (G-10): <path>")` |
| pdflatex exits non-zero | `ReportError("pdflatex failed (exit N).\n<last 25 log lines>")` |
| PDF absent after exit 0 | `ReportError("PDF not found after compilation: <path>")` |

On any pdflatex failure the `.tex` source is preserved for post-mortem inspection.

---

## Test File

`tests/test_report_generator.py`

### Test cases

| ID | Class / Scenario | Expected |
|----|-----------------|----------|
| TC-11-001 | `_escape`: special characters (`& % $ # _ { } ~ ^ \`) | Each character maps to correct LaTeX escape sequence. |
| TC-11-002 | `_escape`: clean strings pass through unchanged | No modification to plain text, paths, numeric strings, or integers. |
| TC-11-003 | `_fmt`: `None` → `"---"` | Returns sentinel regardless of `decimals` argument. |
| TC-11-004 | `_fmt`: `float("nan")` → `"---"` | Same sentinel as `None`. |
| TC-11-005 | `_fmt`: valid float with default 2 decimals | Correct fixed-point string. |
| TC-11-006 | `_fmt`: custom `decimals` argument | Correct precision for 1, 0, and 4 decimal places. |
| TC-11-007 | `_fill_template`: all `__KEY__` placeholders replaced | Single, multiple, and repeated-key cases. |
| TC-11-008 | `_fill_template`: unknown keys silently ignored; absent placeholder remains | No raise; unreferenced key discarded; missing key left as-is. |
| TC-11-009 | `_build_values`: required keys present; correct types and format | All 27 required keys present; all values are `str`; date/time formats correct; positive/no-effect counts match fixture. |
| TC-11-010 | `generate_report`: missing template → `ReportError` | Raises with message matching "template not found". |
| TC-11-011 | `generate_report`: pdflatex absent → `ReportError` | Raises with message matching "pdflatex not found". |
| TC-11-012 | `generate_report`: PDF already exists → `ReportError` (G-10) | Raises with message matching "G-10". |
| TC-11-013 | `generate_report`: `.tex` written with all placeholders replaced | No `__` sequences remain; run date present in content. |
| TC-11-014 | `generate_report`: pdflatex called exactly twice | `subprocess.run` invoked 2 times. |
| TC-11-015 | `generate_report`: auxiliary files removed after compilation | `.aux`, `.log`, `.out`, `.toc` do not exist after successful run. |
| TC-11-016 | `generate_report`: returns PDF `Path` on success | Return value equals `tmp_path / "cpm_ia_report.pdf"` and file exists. |
| TC-11-017 | `generate_report`: pdflatex exits non-zero → `ReportError`; `.tex` preserved | Raises with "pdflatex failed"; `.tex` still on disk. |
| TC-11-018 | `generate_report`: PDF absent after exit 0 → `ReportError` | Raises with "PDF not found after compilation". |
