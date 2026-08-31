# LINKED-TO: [REQ-CPM-IA-P26.0006]
"""
descent_window.py — Adaptive Descent-Window Determination for the CPM-IA component.

Starting from each (visit, point) anchor, builds the maximal non-increasing run of
consecutive marker values, closed by the first rise exceeding epsilon and capped at
n_max points (G-07). Series with no anchor receive a None window entry.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.marker_sequence import Sequences
from src.trigger_detection import TriggerResults

logger = logging.getLogger(__name__)


class DescentError(Exception):
    """Raised when descent-window determination is called with invalid parameters."""


@dataclass(frozen=True)
class DescentWindow:
    """Immutable result of the descent-window determination for one (visit, point) series."""

    window_values: List[float]   # ordered values starting with the anchor
    window_length: int           # == len(window_values)
    truncated_by_n_max: bool     # True when n_max cap forced early stop


DescentWindows = Dict[Tuple[str, str], Optional[DescentWindow]]

# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _build_window(
    seq: List[float],
    anchor_index: int,
    rise_tolerance_epsilon: float,
    n_max: int,
) -> DescentWindow:
    """Slice the descent window from *seq* starting at *anchor_index*."""
    if anchor_index >= len(seq):
        raise DescentError(
            f"Anchor index {anchor_index} out of bounds for sequence of length {len(seq)}"
        )

    window: List[float] = [seq[anchor_index]]
    prev: float = seq[anchor_index]
    truncated_by_n_max = False

    for k in range(anchor_index + 1, len(seq)):
        val = seq[k]

        # 1. Skip NaN — prev retains the last valid value (Decision A: NaN bridging)
        if math.isnan(val):
            continue

        # 2. Significant rise → close window naturally (checked before n_max)
        if val - prev > rise_tolerance_epsilon:
            break

        # 3. G-07 cap — if appending would exceed n_max, mark truncation and stop.
        #    Checked AFTER rise so that a rising value is not counted as a truncation.
        if len(window) >= n_max:
            truncated_by_n_max = True  # Decision B: cap fired before a natural close
            break

        window.append(val)
        prev = val

    return DescentWindow(
        window_values=window,
        window_length=len(window),
        truncated_by_n_max=truncated_by_n_max,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def determine_descent_windows(
    sequences: Sequences,
    trigger_results: TriggerResults,
    rise_tolerance_epsilon: float,
    n_max: int,
) -> DescentWindows:
    """
    Determine the adaptive descent window for every (visit, point) series.

    Args:
        sequences:               Ordered value sequences from build_sequences().
        trigger_results:         Anchor positions from detect_triggers().
        rise_tolerance_epsilon:  Max consecutive increase still considered non-rising (>= 0).
        n_max:                   Hard cap on window length (>= 1, enforces G-07).

    Returns:
        DescentWindows: mapping (visit_id, point_id) -> DescentWindow, or None for
        series with no_cross_marker_effect=True.

    Raises:
        DescentError: when n_max < 1, rise_tolerance_epsilon < 0, or anchor out of bounds.
    """
    if n_max < 1:
        raise DescentError(f"n_max must be >= 1, got {n_max}")
    if rise_tolerance_epsilon < 0:
        raise DescentError(
            f"rise_tolerance_epsilon must be >= 0, got {rise_tolerance_epsilon}"
        )

    windows: DescentWindows = {}

    for (visit, point), result in trigger_results.items():
        if result.no_cross_marker_effect:
            windows[(visit, point)] = None
            continue

        seq = sequences[(visit, point)]
        anchor_index = result.first_positive_index  # type: ignore[arg-type]

        windows[(visit, point)] = _build_window(
            seq, anchor_index, rise_tolerance_epsilon, n_max
        )

    logger.debug(
        "CPM-IA descent windows | total=%d | with_window=%d | truncated=%d",
        len(windows),
        sum(1 for w in windows.values() if w is not None),
        sum(1 for w in windows.values() if w is not None and w.truncated_by_n_max),
    )

    return windows
