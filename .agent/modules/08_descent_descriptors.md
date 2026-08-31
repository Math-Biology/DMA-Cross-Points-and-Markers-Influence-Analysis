# Module 08 — Descent Shape Descriptors
**File:** `src/descent_descriptors.py`
**SR:** REQ-CPM-IA-P26.0008 — Descent Shape Descriptors
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-27 | 20/20 tests pass

---

## Requirement (verbatim)

In addition to the slope, the component compute descriptors characterising the descending curve after the first positive, comprising, as a minimum: the descent depth (difference between the anchor value and the minimum value within the window), the descent length (number of points in the window), and the mean per-step decrease. These descriptors must quantify the magnitude and the extent of the excitation decay.

---

## Functional Boundary

This module computes the three mandatory shape descriptors for each descent window. It depends on Module 06 (windows) and Module 04 (anchor value). It does not compute slope (Module 07) or variance indicators (Module 09).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `descent_windows` | `dict` | From Module 06 (`window_values`, `window_length`). |
| `trigger_results` | `dict` | From Module 04 (`first_positive_value` as anchor). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `descriptors` | `dict` | Mapping from (visit, point) to `{'descent_depth': float, 'descent_length': int, 'mean_per_step_decrease': float}` or `None` if no descent window. |

---

## Behaviour Specification

1. For each (visit, point) where `descent_windows` value is `None`: set `descriptors[(v,p)] = None`.
2. For each (visit, point) with valid window and anchor value `a`:
   a. `descent_depth = a - min(window_values)`.
   b. `descent_length = window_length` (from Module 06 output).
   c. `mean_per_step_decrease = descent_depth / (descent_length - 1)` if `descent_length > 1`, else `0.0`.
3. Return `descriptors`.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `first_positive_value` is None for a non-None window | Raise `DescriptorError("Anchor value missing for (visit, point) with descent window")`. |
| Window contains NaN | Raise `DescriptorError("NaN in descent window for (visit, point)")`. |

---

## Test File

`tests/test_descent_descriptors.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-08-001 | anchor=300, window=[300,250,200,150] | depth=150, length=4, mean_per_step_decrease=50.0. |
| TC-08-002 | Window of length 1 (anchor only) | depth=0, length=1, mean_per_step_decrease=0.0. |
| TC-08-003 | `descent_windows` value is None | `descriptors[(v,p)] = None`. |
| TC-08-004 | Window contains NaN | Raises `DescriptorError`. |
