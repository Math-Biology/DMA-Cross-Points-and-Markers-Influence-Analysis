# Module 04 — All-Positive Trigger Detection
**File:** `src/trigger_detection.py`
**SR:** REQ-CPM-IA-P26.0004 — All-Positive Trigger Detection
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-09-23 | 19/19 tests pass

---

## Requirement (verbatim)

Within each (visit, point) marker sequence, the component detects all markers whose raw percentage variation meets or exceeds the configured positive-detection threshold (`>= threshold_pct`) and designates them as excitation anchors for that series, in the order they appear in the detection sequence. A series containing no threshold-meeting marker must be reported as having no cross-marker effect.

---

## Functional Boundary

This module iterates over the ordered sequences produced by Module 03. For each (visit, point) series it collects all marker positions where `value >= threshold_pct` and returns the complete ordered list of anchors. It does not compute descent metrics.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `sequences` | `Sequences` | From Module 03. |
| `marker_orders` | `PerVisitMarkerOrders` (`Dict[str, List[str]]`) | Per-visit marker lists from Module 03. |
| `threshold_pct` | `float` | From `CpmIaConfig` (required, no default). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `trigger_results` | `TriggerResults` | Mapping `(visit_id, point_id) -> TriggerResult`. |

### TriggerResult fields

| Field | Type | Description |
|-------|------|-------------|
| `anchors` | `List[Anchor]` | Ordered list of all excitation anchors (empty when no_cross_marker_effect). |
| `positives_count` | `int` | `== len(anchors)`. |
| `no_cross_marker_effect` | `bool` | `True` when `anchors` is empty. |

### Anchor fields

| Field | Type | Description |
|-------|------|-------------|
| `marker` | `str` | Marker identifier. |
| `index` | `int` | Position in the per-visit detection sequence. |
| `value` | `float` | Raw percentage variation at this position. |

---

## Behaviour Specification

1. For each `(visit, point)` in `sequences`:
   a. Retrieve `visit_marker_order = marker_orders[visit]`.
   b. Iterate all sequence values in index order; skip NaN values explicitly.
   c. For every value where `value >= threshold_pct`: append `Anchor(marker=visit_marker_order[i], index=i, value=value)` to `anchors`. **Do not break** — continue to the end.
   d. Set `positives_count = len(anchors)`, `no_cross_marker_effect = (positives_count == 0)`.
2. Store each `TriggerResult` in `trigger_results[(visit, point)]` — every key is always written (G-06).
3. Return `trigger_results`.

---

## Guardrails Enforced

- G-05 (updated): ALL threshold-meeting markers (value >= threshold_pct) are collected as anchors in sequence order. The anchors list is immutable for the run.
- G-06: Series with no anchor are flagged `no_cross_marker_effect = True` and included in the output dict.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `threshold_pct <= 0` | Raise `TriggerError("threshold_pct must be positive")`. |
| `sequences` is empty | Return empty dict (no error). |

---

## Test File

`tests/test_trigger_detection.py` — 19 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-04-001 | M1=100, M2=350, M3=400; threshold=300 | `anchors=[Anchor('M2',1,350), Anchor('M3',2,400)]`; `positives_count=2`. |
| TC-04-002 | M1=100, M2=200, M3=250; threshold=300 | `no_cross_marker_effect=True`; `anchors=[]`; `positives_count=0`. |
| TC-04-003 | M1=400, M2=500, M3=350; threshold=300 | All three are anchors; `positives_count=3`; order matches sequence. |
| TC-04-004 | All NaN | `no_cross_marker_effect=True`. |
| TC-04-005 | `threshold_pct=0` | Raises `TriggerError`. |
| TC-04-006 | value == 300.0; threshold=300.0 | `>=` → IS a positive anchor. |
| TC-04-007 | `threshold_pct < 0` | Raises `TriggerError`. |
| TC-04-008 | NaN before and between positives | NaN skipped; correct anchors at non-NaN positions. |
| TC-04-009 | Empty sequences dict | Returns `{}`. |
| TC-04-010 | Multiple (visit, point) pairs, mixed outcomes | Each pair classified independently. |
| TC-04-011 | `TriggerResult` immutability | Frozen dataclass; assignment raises. |
