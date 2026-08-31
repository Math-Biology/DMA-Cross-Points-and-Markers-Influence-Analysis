# Module 09 — Pre/Post Positive Variance Indicator
**File:** `src/variance_indicator.py`
**SR:** REQ-CPM-IA-P26.0009 — Pre/Post Positive Variance Indicator
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-31 | 26/26 tests pass

---

## Requirement (verbatim)

For each (visit, point) series with a first positive, the component compute a dispersion indicator of the marker measurements before and after the anchor, where the "before" segment comprises the markers preceding the first positive in the sequence and the "after" segment comprises the markers within the descent window. The indicator must be expressed as the statistical variance of each segment, enabling comparison of measurement dispersion prior to and following the excitation.

---

## Functional Boundary

This module computes the statistical variance of the "before" and "after" (descent window) segments for each (visit, point) series that has a first positive. It also computes a normalised variance ratio. It depends on Module 03 (full sequence), Module 04 (anchor index), and Module 06 (descent window values).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `Sequences` | From Module 03 (full ordered sequence per (visit, point)). |
| `trigger_results` | `TriggerResults` | From Module 04 (`first_positive_index`). |
| `descent_windows` | `DescentWindows` | From Module 06 (`window_values`). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `variance_indicators` | `VarianceIndicators` | Mapping from `(visit_id, point_id)` to a `VarianceIndicator` frozen dataclass, or `None` if `no_cross_marker_effect=True`. |

### `VarianceIndicator` fields

| Field | Type | Description |
|-------|------|-------------|
| `variance_before` | `Optional[float]` | Sample variance (ddof=1) of the before-segment; `None` when fewer than 2 clean values. |
| `variance_after` | `Optional[float]` | Sample variance (ddof=1) of the after-segment (descent window); `None` when fewer than 2 clean values. |
| `variance_ratio` | `Optional[float]` | `variance_after / variance_before`; `None` when either variance is `None` or `variance_before == 0`. |

---

## Behaviour Specification

1. For each `(visit, point)` with `no_cross_marker_effect = True`: set `variance_indicators[(v,p)] = None`.
2. For each `(visit, point)` with anchor at index `i`:
   a. `before_segment = sequence[0:i]` (markers preceding the anchor, excluding the anchor itself). Remove NaN values.
   b. `after_segment = descent_window_values` (from Module 06, including the anchor at position 0). Remove NaN values defensively.
   c. `variance_before = statistics.variance(before_segment)` if `len(before_segment) >= 2`, else `None`.
   d. `variance_after = statistics.variance(after_segment)` if `len(after_segment) >= 2`, else `None`.
   e. `variance_ratio = variance_after / variance_before` if both are defined and `variance_before > 0`, else `None`.
3. Use population-corrected (sample) variance (`ddof=1`) via Python `statistics.variance`.
4. Return `variance_indicators`.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Anchor at index 0 (no "before" segment) | `variance_before = None`. |
| Window length 1 | `variance_after = None`. |
| `variance_before == 0` | `variance_ratio = None` (avoid division by zero). |

---

## Test File

`tests/test_variance_indicator.py`

### Test cases

| ID | Scenario | Expected |
|----|----------|----------|
| TC-09-001 | before=[100,120], after=[300,250,200] | Correct sample variances; matches `statistics.variance` reference. |
| TC-09-002 | Anchor at index 0 | `variance_before=None`; `variance_after` computed. |
| TC-09-003 | Descent window length 1 | `variance_after=None`; `variance_before` computed. |
| TC-09-004 | `no_cross_marker_effect=True` | `variance_indicators[(v,p)] = None`. |
| TC-09-005 | Before segment has single value | `variance_before=None`. |
| TC-09-006 | NaN in before segment (enough remain after strip) | `variance_before` computed on clean values only. |
| TC-09-007 | Before segment entirely NaN | `variance_before=None`; `variance_after` computed. |
| TC-09-008 | Multiple (visit, point) pairs — mix of None and valid | Correct keys; None for no-effect; valid indicators for positive. |
| TC-09-009 | All entries `no_cross_marker_effect=True` | All indicators `None`. |
| TC-09-010 | `variance_ratio` field | Ratio computed when both valid and before>0; None when before=None, after=None, or before=0; ratio>1 when after more dispersed; ratio<1 when after tighter. |
