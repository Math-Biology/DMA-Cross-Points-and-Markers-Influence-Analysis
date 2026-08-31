# LINKED-TO: [REQ-CPM-IA-P26.0004]
"""
trigger_detection.py — First-Positive Trigger Detection for the CPM-IA component.

For each (visit, point) ordered sequence, identifies the first marker whose raw
percentage variation strictly exceeds threshold_pct (the excitation onset / anchor).
Series with no threshold-exceeding marker are explicitly flagged (G-05, G-06).
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.marker_sequence import PerVisitMarkerOrders, Sequences

logger = logging.getLogger(__name__)


class TriggerError(Exception):
    """Raised when trigger detection is called with an invalid configuration."""


@dataclass(frozen=True)
class TriggerResult:
    """Immutable result record for one (visit, point) series."""

    first_positive_marker: Optional[str]   # marker_id of anchor, or None
    first_positive_index: Optional[int]    # position in per-visit sequence, or None
    first_positive_value: Optional[float]  # raw_pct_variation of anchor, or None
    no_cross_marker_effect: bool           # True when no marker exceeds threshold


TriggerResults = Dict[Tuple[str, str], TriggerResult]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_triggers(
    sequences: Sequences,
    marker_orders: PerVisitMarkerOrders,
    threshold_pct: float,
) -> TriggerResults:
    """
    Scan each (visit, point) sequence and detect the first-positive anchor.

    Args:
        sequences:     Per-(visit, point) ordered value lists from build_sequences().
        marker_orders: Per-visit marker lists from build_sequences(). Each visit's
                       list defines the detection order used to name the anchor.
        threshold_pct: Positive-detection threshold (must be > 0).

    Returns:
        TriggerResults mapping each (visit, point) key to a TriggerResult.
        An empty sequences dict returns an empty TriggerResults without error.

    Raises:
        TriggerError: when threshold_pct <= 0.
    """
    if threshold_pct <= 0:
        raise TriggerError(
            f"threshold_pct must be positive, got {threshold_pct}"
        )

    if not sequences:
        return {}

    results: TriggerResults = {}

    for (visit, point), seq in sequences.items():
        visit_marker_order = marker_orders[visit]
        anchor_marker: Optional[str] = None
        anchor_index: Optional[int] = None
        anchor_value: Optional[float] = None
        found = False

        for i, value in enumerate(seq):
            # Explicit NaN skip — float('nan') > threshold also evaluates False,
            # but the intent must be unambiguous in safety-critical code.
            if math.isnan(value):
                continue
            if value > threshold_pct:   # strictly exceeds (G-05: break on first hit)
                anchor_marker = visit_marker_order[i]
                anchor_index = i
                anchor_value = value
                found = True
                break

        results[(visit, point)] = TriggerResult(
            first_positive_marker=anchor_marker,
            first_positive_index=anchor_index,
            first_positive_value=anchor_value,
            no_cross_marker_effect=not found,
        )

    logger.debug(
        "CPM-IA trigger detection | total_series=%d | positives=%d | no_effect=%d",
        len(results),
        sum(1 for r in results.values() if not r.no_cross_marker_effect),
        sum(1 for r in results.values() if r.no_cross_marker_effect),
    )

    return results
