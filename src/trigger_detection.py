# LINKED-TO: [REQ-CPM-IA-P26.0004]
"""
trigger_detection.py — All-Positive Trigger Detection for the CPM-IA component.

For each (visit, point) ordered sequence, identifies ALL markers whose raw
percentage variation is >= threshold_pct (excitation anchors).
Series with no threshold-meeting marker are explicitly flagged (G-05, G-06).
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.marker_sequence import PerVisitMarkerOrders, Sequences

logger = logging.getLogger(__name__)


class TriggerError(Exception):
    """Raised when trigger detection is called with an invalid configuration."""


@dataclass(frozen=True)
class Anchor:
    """One detected excitation anchor in a (visit, point) series."""
    marker: str
    index: int    # position in the per-visit sequence
    value: float


def _compute_consecutive_runs(anchors: List[Anchor]) -> Tuple[List[int], int]:
    """Map each anchor to the length of its maximal consecutive run.

    Two anchors are consecutive when anchors[i+1].index == anchors[i].index + 1.
    Returns (per_anchor_run_lengths, consecutive_peaks).
    consecutive_peaks = number of anchors belonging to a run of length >= 2.
    """
    if not anchors:
        return [], 0
    run_lengths: List[int] = []
    i = 0
    while i < len(anchors):
        j = i
        while j + 1 < len(anchors) and anchors[j + 1].index == anchors[j].index + 1:
            j += 1
        run_len = j - i + 1
        run_lengths.extend([run_len] * run_len)
        i = j + 1
    consecutive_peaks = sum(1 for rl in run_lengths if rl >= 2)
    return run_lengths, consecutive_peaks


@dataclass(frozen=True)
class TriggerResult:
    """Immutable result record for one (visit, point) series."""

    anchors: List[Anchor]         # ordered list of all anchors (empty when no_cross_marker_effect)
    positives_count: int          # == len(anchors)
    no_cross_marker_effect: bool  # True when anchors is empty
    anchor_run_lengths: List[int] = field(default_factory=list)  # auto-computed
    consecutive_peaks: int = 0                                   # auto-computed

    def __post_init__(self) -> None:
        rl, cp = _compute_consecutive_runs(self.anchors)
        object.__setattr__(self, "anchor_run_lengths", rl)
        object.__setattr__(self, "consecutive_peaks", cp)


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
    Scan each (visit, point) sequence and detect all positive anchors.

    Args:
        sequences:     Per-(visit, point) ordered value lists from build_sequences().
        marker_orders: Per-visit marker lists from build_sequences(). Each visit's
                       list defines the detection order used to name the anchors.
        threshold_pct: Positive-detection threshold (must be > 0).
                       A marker is positive when value >= threshold_pct.

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
        anchors: List[Anchor] = []

        for i, value in enumerate(seq):
            # Skip NaN — intent must be unambiguous in safety-critical code.
            if math.isnan(value):
                continue
            if value >= threshold_pct:   # >= (inclusive threshold crossing)
                anchors.append(Anchor(
                    marker=visit_marker_order[i],
                    index=i,
                    value=value,
                ))

        results[(visit, point)] = TriggerResult(
            anchors=anchors,
            positives_count=len(anchors),
            no_cross_marker_effect=(len(anchors) == 0),
        )

    logger.debug(
        "CPM-IA trigger detection | total_series=%d | positives=%d | no_effect=%d",
        len(results),
        sum(1 for r in results.values() if not r.no_cross_marker_effect),
        sum(1 for r in results.values() if r.no_cross_marker_effect),
    )

    return results
