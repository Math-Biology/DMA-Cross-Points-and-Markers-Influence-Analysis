# Module 09 — Pre/Post Positive Variance Indicator (per anchor)
**File:** `src/variance_indicator.py`
**SR:** REQ-CPM-IA-P26.0009 — Pre/Post Positive Variance Indicator
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-09-23 | 22/22 tests pass

---

## Requirement (verbatim)

For each (visit, point) series with detected anchors, the component computes a dispersion indicator of the marker measurements before and after each anchor, where the "before" segment comprises the markers preceding the anchor in the sequence and the "after" segment comprises the markers within that anchor's descent window. The indicator is expressed as the statistical variance of each segment, enabling comparison of measurement dispersion prior to and following each excitation event.

---

## Functional Boundary

This module computes the statistical variance of the "before" and "after" (descent window) segments for each anchor in every (visit, point) series. The formula is identical across all anchors. It depends on Module 03 (full sequence), Module 04 (anchor indices), and Module 06 (descent window values per anchor).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `Sequences` | Full ordered marker sequences from Module 03. |
| `trigger_results` | `TriggerResults` | Anchor positions from Module 04. |
| `descent_windows` | `DescentWindows` | Per-anchor descent windows from Module 06. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `variance_indicators` | `VarianceIndicators` | `Dict[Tuple[str,str], List[Optional[VarianceIndicator]]]`. Empty list `[]` for no-effect series. One entry per anchor. |

### VarianceIndicator fields (unchanged)

| Field | Type | Description |
|-------|------|-------------|
| `variance_before` | `Optional[float]` | Sample variance (`ddof=1`) of sequence values before the anchor index (NaN removed). `None` if < 2 clean values. |
| `variance_after` | `Optional[float]` | Sample variance of the anchor's descent window values (NaN removed). `None` if < 2 clean values. |
| `variance_ratio` | `Optional[float]` | `variance_after / variance_before`. `None` when either variance is `None` or `variance_before == 0`. |

---

## Behaviour Specification

For each (visit, point) series:
1. If `no_cross_marker_effect = True`: store `[]`.
2. For each anchor i (`anchor = result.anchors[i]`):
   a. `before_clean = [v for v in sequences[key][0:anchor.index] if not isnan(v)]`
   b. `after_clean = [v for v in descent_windows[key][i].window_values if not isnan(v)]`
   c. `variance_before = statistics.variance(before_clean)` if `len(before_clean) >= 2`, else `None`.
   d. `variance_after = statistics.variance(after_clean)` if `len(after_clean) >= 2`, else `None`.
   e. `variance_ratio = variance_after / variance_before` if both defined and `variance_before > 0`, else `None`.
   f. Append `VarianceIndicator(variance_before, variance_after, variance_ratio)`.
3. Store list in `variance_indicators[(visit, point)]`.

---

## Test File

`tests/test_variance_indicator.py` — 22 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-09-001 | Single anchor; sufficient before/after values | `variance_before` and `variance_after` match `statistics.variance` reference. |
| TC-09-002 | Before segment < 2 values | `variance_before = None`. |
| TC-09-003 | After segment (window) < 2 values | `variance_after = None`. |
| TC-09-004 | `no_cross_marker_effect=True` | Returns `[]` for that key. |
| TC-09-005 | Anchor at index 0 | `before_clean = []`; `variance_before = None`. |
| TC-09-006 | NaN in before segment | NaN stripped; variance computed on clean values. |
| TC-09-007 | All before values NaN | `variance_before = None`. |
| TC-09-009 | All keys produce a list in output | No key missing. |
| TC-09-010 | `variance_ratio` computed; `variance_before > 0` | Ratio matches `variance_after / variance_before`. |
| TC-09-011 | Two anchors → two VarianceIndicator entries | List length == 2. |
