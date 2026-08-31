# Module 05 — Positive Census Across Points
**File:** `src/positive_census.py`
**SR:** REQ-CPM-IA-P26.0005 — Positive Census Across Points
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-27 | 10/10 tests pass

---

## Requirement (verbatim)

The component determines, across the whole dataset, how many and which anatomical points present at least one first positive, providing both the count and the identity of the positive points as an explicit output. This census must enable quantification of the prevalence of the cross-marker excitation phenomenon at anatomical-point level.

---

## Functional Boundary

This module aggregates the per-(visit, point) trigger results from Module 04 to the anatomical-point level, counting unique points that have at least one visit with a detected first positive. It produces a standalone census object used by Module 10 for output consolidation.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `trigger_results` | `dict` | From Module 04. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `census` | `dict` | `{'positive_point_count': int, 'positive_points': list[str], 'total_point_count': int}` |

---

## Behaviour Specification

1. Collect all unique anatomical points from `trigger_results` keys.
2. For each anatomical point, determine whether any (visit, point) entry has `no_cross_marker_effect = False`.
3. Collect the identifiers of positive points into `positive_points` (sorted for deterministic output).
4. Set `positive_point_count = len(positive_points)`.
5. Set `total_point_count = len(unique anatomical points)`.
6. Return `census`.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| `trigger_results` is empty | Return census with all counts = 0 and `positive_points = []`. |

---

## Test File

`tests/test_positive_census.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-05-001 | 3 points; P1 has positive, P2 no, P3 has positive | `positive_point_count=2`, `positive_points=['P1','P3']`. |
| TC-05-002 | No points have a positive | `positive_point_count=0`. |
| TC-05-003 | Single (visit, point) with positive | `positive_point_count=1`, `total_point_count=1`. |
| TC-05-004 | Empty `trigger_results` | Returns census with all zeros. |
