# LINKED-TO: [REQ-CPM-IA-P26.0007]
"""
descent_slope.py — Descent Slope Computation for the CPM-IA component.

Computes the OLS linear-regression slope over each descent window using the
closed-form formula stated in REQ-CPM-IA-P26.0007 (G-08: standard OLS only).

Implementation: direct closed-form — see formula below.
Cross-validation: tests verify numerical equivalence against numpy.polyfit.

    slope = (n·Σ(i·yᵢ) − Σi·Σyᵢ) / (n·Σi² − (Σi)²)
    where i = 0, 1, …, L-1  (equally spaced abscissae)  and  n = L
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Tuple

from src.descent_window import DescentWindows

logger = logging.getLogger(__name__)

Slopes = Dict[Tuple[str, str], List[Optional[float]]]


class SlopeError(Exception):
    """Raised when slope computation encounters an invalid window (e.g. NaN values)."""


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _ols_slope(values: list[float]) -> Optional[float]:
    """
    Compute the OLS slope for *values* treated as equally spaced ordinates.

    Returns None for a single-point window (undefined regression) and logs WARNING.
    Raises SlopeError if any NaN is present.

    Formula (from REQ-CPM-IA-P26.0007):
        slope = (n·Σ(i·yᵢ) − Σi·Σyᵢ) / (n·Σi² − (Σi)²)
    """
    n = len(values)

    if any(math.isnan(v) for v in values):
        raise SlopeError(f"NaN found in descent window of length {n}")

    if n == 1:
        logger.warning(
            "Slope undefined for single-point window (L=1); returning None."
        )
        return None

    # Closed-form OLS with x = [0, 1, ..., n-1]
    sum_y = sum(values)
    sum_x = n * (n - 1) // 2            # Σi = n(n-1)/2
    sum_xy = sum(i * values[i] for i in range(n))
    sum_x2 = n * (n - 1) * (2 * n - 1) // 6   # Σi² = n(n-1)(2n-1)/6

    denom = n * sum_x2 - sum_x ** 2     # always > 0 for n >= 2
    return (n * sum_xy - sum_x * sum_y) / denom


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_slopes(descent_windows: DescentWindows) -> Slopes:
    """
    Compute the OLS descent slope for every anchor in every (visit, point) series.

    Args:
        descent_windows: Mapping (visit_id, point_id) -> List[DescentWindow]
                         from determine_descent_windows().

    Returns:
        Slopes: mapping (visit_id, point_id) -> List[Optional[float]].
        Empty list for series with no anchors.
        None entries within the list for single-point windows (slope undefined).

    Raises:
        SlopeError: if a window contains NaN values (should not occur with
        valid upstream data from Module 06).
    """
    slopes: Slopes = {}

    for (visit, point), window_list in descent_windows.items():
        slopes[(visit, point)] = [_ols_slope(w.window_values) for w in window_list]

    logger.debug(
        "CPM-IA slopes computed | total=%d | with_slopes=%d",
        len(slopes),
        sum(1 for sl in slopes.values() if sl),
    )

    return slopes
