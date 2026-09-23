# LINKED-TO: [REQ-CPM-IA-P26.0006]
"""
descent_window.py — Adaptive Descent-Window Determination for the CPM-IA component.

Starting from each (visit, point) anchor, builds the maximal non-increasing run of
consecutive marker values, closed by the first rise exceeding epsilon, by the next
positive anchor, or capped at n_max points (G-07). Series with no anchor receive
an empty list in descent_windows.
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
    """Immutable result of the descent-window determination for one anchor."""

    window_values: List[float]   # ordered values starting with the anchor
    window_length: int           # == len(window_values)
    truncated_by_n_max: bool     # True when n_max cap forced early stop
    window_close_reason: str     # 'rise' | 'next_positive' | 'n_max' | 'end'


DescentWindows = Dict[Tuple[str, str], List[DescentWindow]]
# Empty list [] for series with no_cross_marker_effect=True

# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _build_window(
    seq: List[float],
    anchor_index: int,
    next_anchor_index: Optional[int],
    rise_tolerance_epsilon: float,
    n_max: int,
) -> DescentWindow:
    """Slice one descent window from *seq* starting at *anchor_index*.

    Args:
        seq:               Full (visit, point) sequence.
        anchor_index:      Index of this anchor in seq.
        next_anchor_index: Index of the immediately following anchor (or None).
        rise_tolerance_epsilon: Max consecutive increase allowed without closing.
        n_max:             Hard cap on window length.
    """
    if anchor_index >= len(seq):
        raise DescentError(
            f"Anchor index {anchor_index} out of bounds for sequence of length {len(seq)}"
        )

    window: List[float] = [seq[anchor_index]]
    prev: float = seq[anchor_index]
    truncated_by_n_max = False
    close_reason = "end"

    for k in range(anchor_index + 1, len(seq)):
        val = seq[k]

        # 1. Skip NaN — prev retains the last valid value (Decision A: NaN bridging)
        if math.isnan(val):
            continue

        # 2. Next anchor boundary — close before it
        if next_anchor_index is not None and k == next_anchor_index:
            close_reason = "next_positive"
            break

        # 3. Significant rise → close window naturally (checked before n_max)
        if val - prev > rise_tolerance_epsilon:
            close_reason = "rise"
            break

        # 4. G-07 cap — if appending would exceed n_max, mark truncation and stop.
        if len(window) >= n_max:
            truncated_by_n_max = True
            close_reason = "n_max"
            break

        window.append(val)
        prev = val

    return DescentWindow(
        window_values=window,
        window_length=len(window),
        truncated_by_n_max=truncated_by_n_max,
        window_close_reason=close_reason,
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
    Determine the adaptive descent window for every (visit, point) anchor.

    Args:
        sequences:               Ordered value sequences from build_sequences().
        trigger_results:         Anchor positions from detect_triggers().
        rise_tolerance_epsilon:  Max consecutive increase still considered non-rising (>= 0).
        n_max:                   Hard cap on window length (>= 1, enforces G-07).

    Returns:
        DescentWindows: mapping (visit_id, point_id) -> List[DescentWindow].
        Empty list for series with no_cross_marker_effect=True.

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
            windows[(visit, point)] = []
            continue

        seq = sequences[(visit, point)]
        anchors = result.anchors
        window_list: List[DescentWindow] = []

        for i, anchor in enumerate(anchors):
            next_anchor_index = anchors[i + 1].index if i + 1 < len(anchors) else None
            w = _build_window(seq, anchor.index, next_anchor_index, rise_tolerance_epsilon, n_max)
            window_list.append(w)

        windows[(visit, point)] = window_list

    with_windows = sum(1 for wl in windows.values() if wl)
    truncated = sum(1 for wl in windows.values() for w in wl if w.truncated_by_n_max)

    logger.debug(
        "CPM-IA descent windows | total=%d | with_window=%d | truncated=%d",
        len(windows),
        with_windows,
        truncated,
    )

    return windows
