# Module 06 — Adaptive Descent-Window Determination (per anchor)
**File:** `src/descent_window.py`
**SR:** REQ-CPM-IA-P26.0006 — Adaptive Descent-Window Determination
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-09-23 | 23/23 tests pass

---

## Requirement (verbatim)

For each anchor detected in a (visit, point) series, the component determines an adaptive influence (descent) window. The window starts at the anchor value and extends over successive markers as long as the signal does not rise significantly. The window closes at the first of: a consecutive increase exceeding the configured rise tolerance epsilon; the position of the next positive anchor in the same series; the n_max cap; or the end of the sequence. The closure reason is recorded.

---

## Functional Boundary

This module takes the anchor list from Module 04 and the ordered sequences from Module 03, then slices out one descent window per anchor. It returns one `List[DescentWindow]` per (visit, point) key. It does not compute slope or shape descriptors.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `Sequences` | From Module 03. |
| `trigger_results` | `TriggerResults` | From Module 04 (provides anchor list per (visit, point)). |
| `rise_tolerance_epsilon` | `float` | From `CpmIaConfig`. |
| `n_max` | `int` | From `CpmIaConfig`. Maximum descent window length per anchor. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `descent_windows` | `DescentWindows` | `Dict[Tuple[str,str], List[DescentWindow]]`. Empty list `[]` for series with `no_cross_marker_effect=True`. One `DescentWindow` per anchor. |

### DescentWindow fields

| Field | Type | Description |
|-------|------|-------------|
| `window_values` | `List[float]` | Ordered values starting with the anchor value. |
| `window_length` | `int` | `== len(window_values)`. |
| `truncated_by_n_max` | `bool` | `True` when the n_max cap forced early stop. |
| `window_close_reason` | `str` | `'rise'` / `'next_positive'` / `'n_max'` / `'end'`. |

---

## Behaviour Specification

For each (visit, point) series:
1. If `no_cross_marker_effect = True`: store `[]` in `descent_windows[(visit, point)]`.
2. For each anchor i in `result.anchors`:
   a. `next_anchor_index = anchors[i+1].index` if i+1 < len(anchors), else `None`.
   b. Start: `window = [seq[anchor.index]]`, `prev = anchor.value`, `close_reason = 'end'`.
   c. Iterate `k = anchor.index + 1, ..., len(seq)-1`:
      - **NaN bridging:** if `seq[k]` is NaN, skip (`prev` unchanged — NaN does not consume n_max steps).
      - **Next positive:** if `k == next_anchor_index` → `close_reason = 'next_positive'`; break.
      - **Rise:** if `seq[k] - prev > epsilon` → `close_reason = 'rise'`; break.
      - **n_max cap:** if `len(window) >= n_max` → `truncated_by_n_max = True`; `close_reason = 'n_max'`; break.
      - Otherwise: append `seq[k]` to `window`; `prev = seq[k]`.
   d. Append `DescentWindow(window, len(window), truncated_by_n_max, close_reason)` to `window_list`.
3. Store `window_list` in `descent_windows[(visit, point)]`.

---

## Guardrails Enforced

- G-07: Hard cap at `n_max` points per anchor window.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `n_max < 1` | Raise `DescentError("n_max must be >= 1")`. |
| `rise_tolerance_epsilon < 0` | Raise `DescentError("rise_tolerance_epsilon must be >= 0")`. |
| Anchor index out of bounds | Raise `DescentError("Anchor index out of bounds...")`. |

---

## Test File

`tests/test_descent_window.py` — 23 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-06-001 | Single anchor; descent then rise > ε | `window_close_reason='rise'`; rise value excluded. |
| TC-06-002 | Single anchor; descent longer than n_max | Window truncated; `truncated_by_n_max=True`; `close_reason='n_max'`. |
| TC-06-003 | Anchor is last element | `window=[anchor_value]`; `close_reason='end'`. |
| TC-06-004 | Rise at first step after anchor | `window=[anchor_value]`; `close_reason='rise'`. |
| TC-06-005 | `no_cross_marker_effect=True` | `descent_windows[(v,p)] == []`. |
| TC-06-006 | `n_max < 1` | Raises `DescentError`. |
| TC-06-007 | Two anchors; no rise between them | First window closes at `next_positive`; second closes at `end`. |
| TC-06-008 | Two adjacent anchors | Two windows of length 1 each; `close_reason='next_positive'` / `'end'`. |
| TC-06-009 | NaN between anchor and next value | NaN bridged; `prev` retained; window continues. |
| TC-06-010 | `window_close_reason` correctness across all four cases | Each reason code verified in isolation. |
