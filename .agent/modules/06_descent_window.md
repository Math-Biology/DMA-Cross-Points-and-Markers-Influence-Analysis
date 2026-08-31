# Module 06 — Adaptive Descent-Window Determination
**File:** `src/descent_window.py`
**SR:** REQ-CPM-IA-P26.0006 — Adaptive Descent-Window Determination
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-27 | 21/21 tests pass

---

## Requirement (verbatim)

Starting from the first positive of each (visit, point) series, the component determines the influence (descent) window as the anchor followed by the maximal initial run of non-increasing consecutive marker measurements. The window must be closed at the first significant rise — defined as the first consecutive increase exceeding the configured rise tolerance epsilon — which marks the end of the positive's influence, and shall in any case be truncated to at most N_max points to prevent an excessively long descent. The number of points retained must therefore be adaptive to the actual length of the descent preceding the rise.

---

## Functional Boundary

This module takes the anchor position from Module 04 and the ordered sequence from Module 03, then slices out the descent window. It returns the window (as a list of values) and its metadata. It does not compute slope or shape descriptors.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `dict` | From Module 03. |
| `trigger_results` | `dict` | From Module 04 (provides anchor index per (visit, point)). |
| `rise_tolerance_epsilon` | `float` | From `CpmIaConfig`. |
| `n_max` | `int` | From `CpmIaConfig`. Maximum number of descent points. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `descent_windows` | `dict` | Mapping from (visit, point) to `{'window_values': list[float], 'window_length': int, 'truncated_by_n_max': bool}` or `None` if no anchor. |

---

## Behaviour Specification

1. For each (visit, point) with `no_cross_marker_effect = True`: store `None` in `descent_windows`.
2. For each (visit, point) with a valid anchor at index `i`:
   a. Start with `window = [sequence[i]]` (the anchor value itself).
   b. Iterate subsequent positions `i+1, i+2, ...` (skipping NaN values).
   c. Append each value while the consecutive increase does not exceed `epsilon` (i.e., `value[k] - value[k-1] <= epsilon`).
   d. Stop at the first position where `value[k] - value[k-1] > epsilon` (significant rise).
   e. Truncate `window` to `n_max` points if `len(window) > n_max`.
   f. Record `truncated_by_n_max = True` if truncation occurred.
3. Return `descent_windows`.

---

## Guardrails Enforced

- G-07: Descent window must be truncated at `n_max` points regardless of actual descent length.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `n_max < 1` | Raise `DescentError("n_max must be >= 1")`. |
| `rise_tolerance_epsilon < 0` | Raise `DescentError("rise_tolerance_epsilon must be >= 0")`. |
| Anchor index out of bounds | Raise `DescentError("Anchor index out of bounds for (visit, point)")`. |

---

## Test File

`tests/test_descent_window.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-06-001 | Anchor=300, then 250, 200, 300 (rise>epsilon); epsilon=5 | Window = [300, 250, 200]. |
| TC-06-002 | Pure monotone descent; window longer than n_max=3 | Window truncated to 3; `truncated_by_n_max=True`. |
| TC-06-003 | Anchor is last element | Window = [anchor_value]; length=1. |
| TC-06-004 | Rise at first step (value[i+1] > anchor + epsilon) | Window = [anchor_value]; length=1. |
| TC-06-005 | `no_cross_marker_effect=True` | `descent_windows[(v,p)] = None`. |
| TC-06-006 | `n_max < 1` | Raises `DescentError`. |
