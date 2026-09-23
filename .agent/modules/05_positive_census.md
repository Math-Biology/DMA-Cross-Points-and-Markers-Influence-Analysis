# Module 05 — Positive Census Across Points
**File:** `src/positive_census.py`
**SR:** REQ-CPM-IA-P26.0005 — Positive Census Across Points
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-09-23 | 13/13 tests pass

---

## Requirement (verbatim)

The component determines, across the whole dataset, how many and which anatomical points present at least one positive anchor, providing both the count and the identity of the positive points as an explicit output. This census must enable quantification of the prevalence of the cross-marker excitation phenomenon at anatomical-point level.

---

## Functional Boundary

This module aggregates the per-(visit, point) trigger results from Module 04 to the anatomical-point level, counting unique points that have at least one visit with at least one detected anchor. It also computes the total anchor count across the dataset. It produces a standalone census object used by Module 10 for output consolidation.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `trigger_results` | `TriggerResults` | Mapping `(visit_id, point_id) -> TriggerResult` from Module 04. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `census` | `PointCensus` | Frozen dataclass with census results. |

### PointCensus fields

| Field | Type | Description |
|-------|------|-------------|
| `positive_point_count` | `int` | Number of unique points with at least one anchor in any visit. |
| `positive_points` | `List[str]` | Sorted identifiers of those points. |
| `total_point_count` | `int` | Total unique anatomical points across the dataset. |
| `total_positives_count` | `int` | Sum of `positives_count` across all (visit, point) series. |

---

## Behaviour Specification

1. Collect all unique anatomical points (`total_point_count`).
2. Identify points where at least one `(visit, point)` entry has `no_cross_marker_effect = False`.
3. `positive_points = sorted(positive_set)` — sorted for deterministic output (unlike G-04 which forbids sorting).
4. `total_positives_count = sum(r.positives_count for r in trigger_results.values())`.
5. Empty input returns `PointCensus(0, [], 0, 0)`.

---

## Test File

`tests/test_positive_census.py` — 13 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-05-001 | 2 visits x 2 points; all positive | `positive_point_count=2`; `total_positives_count >= 2`. |
| TC-05-002 | One point has no positive in any visit | `positive_point_count=1`; negative point excluded. |
| TC-05-003 | Empty input | `PointCensus(0, [], 0, 0)`. |
| TC-05-004 | `positive_points` is sorted | Alphabetical order verified. |
| TC-05-005 | `total_positives_count` matches sum of all `positives_count` values | Numerical equality. |
