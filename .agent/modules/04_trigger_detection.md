# Module 04 — First-Positive Trigger Detection
**File:** `src/trigger_detection.py`
**SR:** REQ-CPM-IA-P26.0004 — First-Positive Trigger Detection
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-31 | 15/15 tests pass

---

## Requirement (verbatim)

Within each (visit, point) marker sequence, the component detects the first marker whose raw percentage variation exceeds the configured positive-detection threshold (default 300 %) and shall designate it as the first positive, i.e. the excitation onset, for that series. Only the first threshold-exceeding marker serves as the anchor for the subsequent influence analysis; later threshold-exceeding markers must not define new anchors. A series containing no threshold-exceeding marker must be reported as having no cross-marker effect.

---

## Functional Boundary

This module iterates over the ordered sequences produced by Module 03. For each (visit, point) series it identifies the index and value of the first marker whose `raw_variation > threshold_pct` and returns this as the anchor. If no such marker exists it flags the series accordingly. It does not compute descent metrics.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `Sequences` | From Module 03. |
| `marker_orders` | `PerVisitMarkerOrders` (`Dict[str, List[str]]`) | Per-visit marker lists from Module 03. Used to resolve the anchor's marker identifier from its sequence index within the correct visit's detection order. |
| `threshold_pct` | `float` | From `CpmIaConfig` (default 300.0). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `trigger_results` | `TriggerResults` | Mapping from `(visit_id, point_id)` to a `TriggerResult` frozen dataclass containing: `first_positive_marker` (str or None), `first_positive_index` (int or None), `first_positive_value` (float or None), `no_cross_marker_effect` (bool). |

---

## Behaviour Specification

1. For each `(visit, point)` in `sequences`:
   a. Retrieve `visit_marker_order = marker_orders[visit]`.
   b. Iterate sequence values in index order; skip NaN values explicitly.
   c. On the first value where `value > threshold_pct`: record `anchor_marker = visit_marker_order[i]`, `anchor_index = i`, `anchor_value = value`. Set `no_cross_marker_effect = False`. Break immediately (G-05).
   d. If no value exceeds `threshold_pct`: set all anchor fields to `None`, `no_cross_marker_effect = True`.
2. Store each `TriggerResult` in `trigger_results[(visit, point)]` — every key is always written (G-06).
3. Return `trigger_results`.

---

## Guardrails Enforced

- G-05: Only the first exceedance is recorded as anchor; the loop breaks after the first detection.
- G-06: Series with no threshold-exceeding marker are flagged `no_cross_marker_effect = True` and included in the output dict.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `threshold_pct <= 0` | Raise `TriggerError("threshold_pct must be positive")`. |
| `sequences` is empty | Return empty dict (no error; upstream Module 03 would have raised). |

---

## Test File

`tests/test_trigger_detection.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-04-001 | M1=100, M2=350, M3=400; threshold=300 | `first_positive_marker='M2'`, `first_positive_index=1`. |
| TC-04-002 | M1=100, M2=200, M3=250; threshold=300 | `no_cross_marker_effect=True`. |
| TC-04-003 | M1=400, M2=500; threshold=300 | First positive is M1 (index 0); M2 not used as anchor. |
| TC-04-004 | All NaN | `no_cross_marker_effect=True`. |
| TC-04-005 | `threshold_pct=0` | Raises `TriggerError`. |
