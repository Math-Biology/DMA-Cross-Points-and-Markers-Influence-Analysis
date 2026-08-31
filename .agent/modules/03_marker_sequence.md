# Module 03 — Marker Sequence Reconstruction
**File:** `src/marker_sequence.py`
**SR:** REQ-CPM-IA-P26.0003 — Marker Sequence Reconstruction
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-31 | 17/17 tests pass

---

## Requirement (verbatim)

For each (visit, anatomical point) pair, the component reconstructs the ordered sequence of marker measurements that defines the analysis axis along which cross-marker influence is evaluated. The marker acquisition order must be derived deterministically from the order of first appearance of each marker in the input dataset and applied consistently to every (visit, point) series, so that the notions of measurement "preceding" and "subsequent" to a given marker are unambiguously defined.

---

## Functional Boundary

This module derives a **per-visit canonical marker order** — independently for each visit, based on the order of first appearance of markers within that visit's rows — and applies it to produce an ordered value sequence for every (visit, point) pair. Each visit maintains its own independent ordering; two visits may detect the same markers in different temporal sequences. This preserves the temporal detection order within each visit, which is required for correct cross-marker influence attribution (G-04). No analytical computation is performed here.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `df` | `pd.DataFrame` | Validated long-format DataFrame from Module 02. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `per_visit_orders` | `PerVisitMarkerOrders` (`Dict[str, List[str]]`) | Mapping from `visit_id` to the ordered list of marker identifiers in temporal detection order for that visit. |
| `sequences` | `Sequences` (`Dict[Tuple[str, str], List[float]]`) | Mapping from `(visit_id, point_id)` to an ordered list of raw percentage variation values, aligned to that visit's `per_visit_orders` entry. Missing marker values are filled with `float('nan')`. |

---

## Behaviour Specification

1. Remove exact duplicate rows (same visit, point, marker, and value — including NaN/NaN pairs) before sequence construction. Log the count of removed rows at WARNING level.
2. For each visit independently, derive the canonical marker order by scanning that visit's rows in their original order and collecting each unique marker value on first encounter (`dict.fromkeys()` pattern). Store as `per_visit_orders[visit_id]`. Never substitute `sorted()`, `set()`, or `.unique()` — those destroy temporal ordering (G-04).
3. For each unique (visit, point) pair, build a value list aligned to `per_visit_orders[visit_id]`: iterate the visit's marker order and look up each marker's value from the group; fill positions where the marker was not measured at this point with `float('nan')`.
4. After exact-dup removal, any remaining duplicate marker within a (visit, point) group carries a conflicting value — raise `SequenceError` with the row index.
5. Log the number of derived visits and (visit, point) pairs at DEBUG level.
6. Return `(per_visit_orders, sequences)`.

---

## Determinism Constraint (Guardrail G-04)

The ordering algorithm must rely exclusively on the row position of each marker's first occurrence within each visit's subset of `df`. No `sorted()`, `set()`, `.unique()`, or locale-sensitive comparison may be used. The correct primitive: iterate `df[COL_MARKER]` per-visit row-by-row, append to an ordered collection (`dict.fromkeys()` pattern) on first encounter.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Empty DataFrame | Raise `SequenceError("Empty input dataset; cannot derive marker order")`. |
| Same (visit, point, marker) triplet with two different values (after exact-dup removal) | Raise `SequenceError("Conflicting values for (visit, point, marker) at row <idx>: ...")`. |

---

## Guardrails Enforced

- G-04: Order of first appearance within each visit only; no sorting.

---

## Test File

`tests/test_marker_sequence.py`

### Test cases

| ID | Scenario | Expected |
|----|----------|----------|
| TC-03-001 | 3 markers in rows M1, M2, M3 for visit V1 | `per_visit_orders["V1"] == ["M1","M2","M3"]`; sequence aligned correctly. |
| TC-03-002 | First appearances within V1: M2, M1, M3 | `per_visit_orders["V1"] == ["M2","M1","M3"]`; not alphabetically sorted. |
| TC-03-003 | (V1, P2) missing M2; V2 has only M1 | `sequences[("V1","P2")][1]` is NaN; `sequences[("V2","P2")]` has length 1 (no padding for markers absent from V2). |
| TC-03-004 | Duplicate (V1, P1, M1) with different values | Raises `SequenceError` with "Conflicting values" and row index. |
| TC-03-005 | Empty DataFrame | Raises `SequenceError("Empty input dataset")`. |
| TC-03-006 | Single data row | `per_visit_orders == {"V1": ["M1"]}`; `sequences == {("V1","P1"): [150.0]}`. |
| TC-03-007 | 2 visits with different detection orders (V1: M1,M2,M3; V2: M2,M1,M3) | Each visit's sequence uses its own order; index i maps to `per_visit_orders[visit][i]` for every pair. |
| TC-03-008 | Full mock (2 visits x 4 markers x 2 points); exact duplicate rows; exact duplicate NaN rows | 4 sequences per visit, all length 4, no NaN; exact duplicates removed silently. |
| TC-03-009 | Conflicting values (different numbers or NaN vs number for same triplet) | Raises `SequenceError("Conflicting values")`. |
