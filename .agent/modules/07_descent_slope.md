# Module 07 — Descent Slope Computation
**File:** `src/descent_slope.py`
**SR:** REQ-CPM-IA-P26.0007 — Descent Slope Computation
**Linked GR:** REQ-G-P26.0018
**Status:** Complete — 2026-08-27 | 17/17 tests pass

---

## Requirement (verbatim)

For each (visit, point) series with an identified descent window, the component computes the slope (rate of decrease) of the descending curve over that window, treating the marker positions as equally spaced abscissae. The slope must be obtained by the standard least-squares linear-regression estimate over the window's points, so that the resulting value expresses the average percentage-point change per marker step; for a minimal window of two points this estimate coincides with the elementary secant slope.

---

## Functional Boundary

This module consumes the descent windows from Module 06 and computes the OLS linear regression slope over each window. It returns only the slope value per (visit, point). Shape descriptors are handled by Module 08.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `descent_windows` | `dict` | From Module 06. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `slopes` | `dict` | Mapping from (visit, point) to `float` slope value (percentage-points per marker step), or `None` if no descent window. |

---

## Behaviour Specification

1. For each (visit, point) where `descent_windows` value is `None`: set `slopes[(v,p)] = None`.
2. For each (visit, point) with a valid window of length L:
   a. Define abscissae `x = [0, 1, 2, ..., L-1]` (equally spaced).
   b. Define ordinates `y = window_values`.
   c. Compute the OLS slope: `slope = (n*sum(x*y) - sum(x)*sum(y)) / (n*sum(x^2) - sum(x)^2)` where `n = L`.
   d. For L=1: slope is undefined (cannot regress on a single point); set `slope = None` and log a WARNING.
   e. For L=2: the formula coincides with the elementary secant slope.
3. Return `slopes`.

---

## Guardrails Enforced

- G-08: Standard OLS least-squares must be used. No alternative estimators (robust regression, Theil-Sen, etc.) are permitted.

---

## Implementation Note

The OLS formula may be implemented directly (closed-form) or via `numpy.polyfit(x, y, 1)` / `scipy.stats.linregress`. Either is acceptable as long as the result is numerically equivalent to standard OLS. Document the chosen implementation in the source file.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Window of length 1 | `slope = None`; emit WARNING log. |
| Window contains NaN after Module 06 | Raise `SlopeError("NaN in descent window for (visit, point)")`. |

---

## Test File

`tests/test_descent_slope.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-07-001 | Window = [300, 200, 100] (perfect linear descent) | `slope = -100.0`. |
| TC-07-002 | Window = [300, 250] (two points) | `slope = -50.0` (secant). |
| TC-07-003 | Window of length 1 | `slope = None`; WARNING logged. |
| TC-07-004 | `descent_windows` value is None | `slopes[(v,p)] = None`. |
| TC-07-005 | Non-linear window (OLS estimate) | Slope matches `numpy.polyfit` reference value. |
