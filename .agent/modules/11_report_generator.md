# Module 11 — Automated PDF Run Report
**File:** `src/report_generator.py`
**SR:** REQ-CPM-IA-P26.0011 — Automated PDF Run Report
**Template:** `data/templates/cpm_ia_report.tex.template`
**Status:** Complete — 2026-09-23 | 33/33 tests pass

---

## Requirement (verbatim)

The component shall automatically generate a PDF run report at the end of each pipeline execution. The report shall contain the run metadata (date, time, configuration parameters), a data quality summary, a summary of dataset statistics, a description of the algorithm and its processing steps, and per-point results tables. All numeric values in the report shall be read directly from pipeline outputs and configuration; no value shall be hard-coded in the report template or generator code.

---

## Functional Boundary

Final pipeline step (after Module 10). Receives consolidated DataFrames, all intermediate outputs, and the data quality report from Module 02. Fills a LaTeX template with computed values and compiles to PDF via two pdflatex passes. On failure the `.tex` source is preserved; auxiliary files are removed on success.

---

## Interface

```python
def generate_report(
    df_detail: pd.DataFrame,
    df_agg: pd.DataFrame,
    trigger_results: TriggerResults,
    census: PointCensus,
    descent_windows: DescentWindows,
    marker_orders: PerVisitMarkerOrders,
    config: CpmIaConfig,
    run_dt: datetime,
    dq_report: DataQualityReport,   # new parameter (Rev 00.01)
) -> Path:
```

---

## Template Placeholders

| Placeholder | Content |
|-------------|---------|
| `__RUN_DATE__`, `__RUN_TIME__` | UTC datetime of pipeline start |
| `__INPUT_PATH__` | `config.input_description()` |
| `__OUTPUT_PATH__`, `__OUTPUT_LABEL_DETAIL__`, `__OUTPUT_LABEL_AGGREGATED__` | From config |
| `__THRESHOLD_PCT__`, `__RISE_EPSILON__`, `__N_MAX__` | From config |
| `__TOTAL_VISITS__`, `__TOTAL_POINTS__`, `__TOTAL_MARKERS__`, `__TOTAL_SERIES__` | Dataset dimensions |
| `__POSITIVE_SERIES__`, `__NO_EFFECT_SERIES__`, `__POSITIVE_RATE__`, `__NO_EFFECT_RATE__` | Series-level stats |
| `__POSITIVE_POINTS__`, `__NO_EFFECT_POINTS__`, `__TOTAL_POINT_COUNT__`, `__POSITIVE_POINTS_RATE__` | Point-level stats |
| `__TOTAL_ANCHORS__` | `census.total_positives_count` |
| `__TRUNCATED_COUNT__`, `__TRUNCATED_RATE__` | Windows truncated at n_max |
| `__DQ_TOTAL_ROWS__`, `__DQ_DROPPED_EMPTY__`, `__DQ_INVALID_POINTS__`, `__DQ_INVALID_ROWS__` | Data quality stats from `dq_report` |
| `__AGG_TABLE_COUNTS__` | LaTeX rows for per-point visit counts table |
| `__AGG_TABLE_MEDIANS__` | LaTeX rows for per-point descent medians table |
| `__ANCHOR_TABLE_ROWS__` | LaTeX rows for per-(point, anchor_marker) frequency table |
| `__ANCHOR_TABLE_THRESHOLD__` | Minimum share (%) for anchor table inclusion |

---

## Behaviour Specification

1. Check template exists; check pdflatex on PATH.
2. Check PDF output path does not already exist (G-10).
3. Compute all placeholder values from pipeline outputs and `dq_report`.
4. Fill template via `__KEY__` substitution; write `.tex` file.
5. Run pdflatex twice for correct TOC page numbers.
6. Remove auxiliary files (`.aux`, `.log`, `.out`, `.toc`) on success.
7. Raise `ReportError` if PDF not present after compilation.

---

## Guardrails Enforced

- G-10: Raise `ReportError` if PDF already exists before compilation.

---

## LaTeX Safety

- C1 control characters (U+0080–U+009F) stripped before LaTeX escaping (`_C1_CTRL_DEL`).
- LaTeX special characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`) escaped.
- Both transforms applied in `_escape(value)`.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Template not found | Raise `ReportError("LaTeX template not found: ...")`. |
| pdflatex not on PATH | Raise `ReportError("pdflatex not found on PATH...")`. |
| PDF already exists | Raise `ReportError("Report PDF already exists (G-10): ...")`. |
| pdflatex exits non-zero | Raise `ReportError("pdflatex failed...")` with last 25 log lines. |

---

## Test File

`tests/test_report_generator.py` — 33 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-11-001 | All placeholders filled | No `__...__` string remaining in output `.tex`. |
| TC-11-002 | `dq_report` values appear in `.tex` | DQ placeholder values match DataQualityReport fields. |
| TC-11-003 | `anchor_marker` column used in anchor table | Not `first_positive_marker`. |
| TC-11-004 | Template not found | Raises `ReportError`. |
| TC-11-005 | PDF already exists | Raises `ReportError`. |
| TC-11-006 | LaTeX special chars in marker name | Correctly escaped in output. |
| TC-11-007 | C1 control char in marker name | Stripped before escaping. |
| TC-11-008 | `_fmt(None)` | Returns `'---'`. |
| TC-11-009 | `_escape` | Correct substitution for all special chars. |
