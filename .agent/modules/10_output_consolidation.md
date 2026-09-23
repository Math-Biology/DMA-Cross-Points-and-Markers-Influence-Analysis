# Module 10 — Consolidated Tidy Output and Per-Point Aggregation
**File:** `src/output_consolidation.py`
**SR:** REQ-CPM-IA-P26.0010 — Consolidated Tidy Output and Per-Point Aggregation
**Linked GR:** REQ-G-P26.0031
**Status:** Complete — 2026-09-23 | 25/25 tests pass

---

## Requirement (verbatim)

The component consolidates its results into tidy (long-format) outputs at two levels: a per-(visit, point, anchor) record carrying the anchor identity, the descent-window characteristics (slope, depth, length, mean per-step decrease, window close reason) and the pre/post variance indicators; and a per-point aggregation across all visits summarising the prevalence of positives, the median number of anchors per visit, and the central tendency (median) of the descent metrics across all anchors. Each output record must be uniquely identified by its grouping keys together with the relevant visit metadata.

---

## Functional Boundary

Final stage. Assembles outputs of Modules 04–09 and 05 into two tidy DataFrames and writes them to disk. No analytical computation.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `df_raw` | `pd.DataFrame` | From Module 02 (provides visit metadata columns). |
| `trigger_results` | `TriggerResults` | From Module 04. |
| `census` | `PointCensus` | From Module 05 (cross-validation only). |
| `descent_windows` | `DescentWindows` | From Module 06 (needed for `window_close_reason`). |
| `slopes` | `Slopes` | From Module 07. |
| `descriptors` | `Descriptors` | From Module 08. |
| `variance_indicators` | `VarianceIndicators` | From Module 09. |
| `config` | `CpmIaConfig` | Output paths and label suffixes. |

---

## Output 1: Per-(visit, point, anchor) Detail Table

One row per anchor. Series with no positives produce one row with `no_cross_marker_effect=True` and anchor fields set to `None`.

| Column | Source |
|--------|--------|
| visit metadata columns | `df_raw` |
| `point` | key |
| `anchor_rank` | 1..k (1-indexed position of anchor in series) |
| `anchor_marker` | `Anchor.marker` (Module 04) |
| `anchor_value` | `Anchor.value` (Module 04) |
| `anchor_index` | `Anchor.index` (Module 04) |
| `positives_count` | `TriggerResult.positives_count` (Module 04) — same for all anchor rows of a series |
| `no_cross_marker_effect` | Module 04 |
| `descent_slope` | Module 07 |
| `descent_depth` | Module 08 |
| `descent_length` | Module 08 |
| `mean_per_step_decrease` | Module 08 |
| `window_close_reason` | Module 06 |
| `variance_before` | Module 09 |
| `variance_after` | Module 09 |
| `variance_ratio` | Module 09 |

**Unique key (G-09):** `(visit_id, point, anchor_marker)`.

---

## Output 2: Per-Point Aggregation Table

One row per unique anatomical point.

| Column | Content |
|--------|---------|
| `point` | Anatomical point identifier |
| `total_visit_count` | Unique visits that include this point |
| `positive_visit_count` | Visits with `no_cross_marker_effect=False` for this point |
| `positive_prevalence` | `positive_visit_count / total_visit_count` |
| `median_positives_count` | Median of `positives_count` per positive (visit, point) pair |
| `median_descent_slope` | Median over all anchor rows for this point |
| `median_descent_depth` | Median over all anchor rows for this point |
| `median_descent_length` | Median over all anchor rows for this point |
| `median_mean_per_step_decrease` | Median over all anchor rows for this point |

---

## Guardrails Enforced

- G-09: Unique key `(visit_id, point, anchor_marker)`. `OutputError` on violation.
- G-10: `OutputError` if target file already exists.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Output path does not exist | Create directory; log WARNING. |
| Output file already exists | Raise `OutputError("Output file already exists: <path>")`. |
| Metadata join failure | Raise `OutputError("Join failure: ...")`. |
| G-09 uniqueness violated | Raise `OutputError("Duplicate ... rows — G-09 uniqueness violated")`. |

---

## Test File

`tests/test_output_consolidation.py` — 25 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-10-001 | 2 visits x 2 points; each with 1 anchor | Detail CSV has 4 rows; aggregation has 2 rows. |
| TC-10-002 | One (visit, point) with `no_cross_marker_effect=True` | One row with `no_cross_marker_effect=True` and anchor fields None. |
| TC-10-003 | Output file already exists | Raises `OutputError`. |
| TC-10-004 | Multi-anchor series | Detail rows = sum of anchor counts + no-effect rows. |
| TC-10-005 | `positives_count` repeated on all anchor rows of a series | Same value for all rows of (visit, point). |
| TC-10-006 | `median_positives_count` in aggregation | Median of per-(visit, point) positives_count for positive visits. |
| TC-10-007 | G-09 uniqueness on `(visit_id, point, anchor_marker)` | No duplicates in detail output. |
