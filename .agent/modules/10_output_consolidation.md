# Module 10 — Consolidated Tidy Output and Per-Point Aggregation
**File:** `src/output_consolidation.py`
**SR:** REQ-CPM-IA-P26.0010 — Consolidated Tidy Output and Per-Point Aggregation
**Linked GR:** REQ-G-P26.0031
**Status:** Complete — 2026-08-31 | 25/25 tests pass

---

## Requirement (verbatim)

The component consolidate its results into tidy (long-format) outputs at two levels: a per-(visit, point) record carrying the first-positive anchor, the descent-window characteristics (slope, depth, length, mean per-step decrease) and the pre/post variance indicators; and a per-point aggregation across all visits summarising the prevalence of positives and the central tendency (e.g. median) of the descent metrics. Each output record must be uniquely identified by its grouping keys together with the relevant visit metadata.

---

## Functional Boundary

This module is the final stage. It assembles the outputs of Modules 04-09 and Module 05 into two tidy DataFrames and writes them to disk using the paths and suffixes from `CpmIaConfig`. It does not perform any analytical computation — it only assembles and serialises results.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `df_raw` | `pd.DataFrame` | Original validated DataFrame from Module 02 (provides visit metadata columns). |
| `trigger_results` | `dict` | From Module 04. |
| `census` | `dict` | From Module 05. |
| `descent_windows` | `dict` | From Module 06. |
| `slopes` | `dict` | From Module 07. |
| `descriptors` | `dict` | From Module 08. |
| `variance_indicators` | `dict` | From Module 09. |
| `config` | `CpmIaConfig` | For output paths and label suffixes. |

---

## Outputs (files written to disk)

| File | Content |
|------|---------|
| `{output_path}/{output_label_detail}.csv` | Per-(visit, point) tidy record. |
| `{output_path}/{output_label_aggregated}.csv` | Per-point aggregated record. |

---

## Output 1: Per-(visit, point) Detail Table

One row per (visit, anatomical point). Columns:

| Column | Source |
|--------|--------|
| visit metadata columns | `df_raw` |
| `point` | key |
| `first_positive_marker` | Module 04 |
| `first_positive_value` | Module 04 |
| `no_cross_marker_effect` | Module 04 |
| `descent_slope` | Module 07 |
| `descent_depth` | Module 08 |
| `descent_length` | Module 08 |
| `mean_per_step_decrease` | Module 08 |
| `variance_before` | Module 09 |
| `variance_after` | Module 09 |
| `variance_ratio` | Module 09 |

---

## Output 2: Per-Point Aggregation Table

One row per unique anatomical point. Columns:

| Column | Content |
|--------|---------|
| `point` | Anatomical point identifier |
| `positive_visit_count` | Number of visits with a first positive at this point |
| `total_visit_count` | Total visits for this point |
| `positive_prevalence` | `positive_visit_count / total_visit_count` |
| `median_descent_slope` | Median of `descent_slope` over positive visits |
| `median_descent_depth` | Median of `descent_depth` over positive visits |
| `median_descent_length` | Median of `descent_length` over positive visits |
| `median_mean_per_step_decrease` | Median of `mean_per_step_decrease` over positive visits |

---

## Behaviour Specification

1. Build the detail DataFrame from all (visit, point) pairs. Merge visit metadata from `df_raw` on (visit, point) keys. Join all computed metrics.
2. Build the aggregation DataFrame by grouping the detail DataFrame on `point` and computing the statistics above. `census` values must be consistent with aggregation counts.
3. Write both DataFrames to CSV (UTF-8, comma-separated) at the configured paths. Do not overwrite existing files with the same name silently — raise `OutputError` if the target file already exists.
4. Log file paths and row counts at INFO level.

---

## Guardrails Enforced

- G-09: All outputs must be in long (tidy) format, uniquely identified by grouping keys + visit metadata.
- G-10: Raise `OutputError` if an output file already exists at the target path.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Output path does not exist | Create directory; log WARNING. |
| Output file already exists | Raise `OutputError("Output file already exists: <path>")`. |
| Visit metadata join yields NaN for a key | Raise `OutputError("Join failure: missing visit metadata for (visit, point)")`. |

---

## Test File

`tests/test_output_consolidation.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-10-001 | 2 visits x 2 points; all with positives | Detail CSV has 4 rows; aggregation CSV has 2 rows. |
| TC-10-002 | One (visit, point) with `no_cross_marker_effect=True` | Row present in detail with `no_cross_marker_effect=True` and NaN metrics. |
| TC-10-003 | Output file already exists | Raises `OutputError`. |
| TC-10-004 | Verify aggregation medians match manual calculation | Numerical equality within floating-point tolerance. |
| TC-10-005 | Verify unique identification: duplicate (visit, point) keys | Raises `OutputError` on join or upstream duplicate detection. |
