# LINKED-TO: [REQ-CPM-IA-P26.0009]
"""
variance_indicator.py — Pre/Post Positive Variance Indicator for the CPM-IA component.

For each (visit, point) series with a detected first positive, computes the sample
variance (ddof=1) of two segments (REQ-CPM-IA-P26.0009):
  - before_segment: full-sequence values preceding the anchor (NaN removed)
  - after_segment:  descent window values (Module 06, NaN removed defensively)

Also computes variance_ratio = variance_after / variance_before as a normalised
indicator of how much the signal variability changes after the excitation onset.

Returns None for a field when the cleaned segment has fewer than 2 points.
variance_ratio is None when either variance is None or variance_before == 0.
Returns None for the whole entry when no_cross_marker_effect=True.
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from src.descent_window import DescentWindows
from src.marker_sequence import Sequences
from src.trigger_detection import TriggerResults

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VarianceIndicator:
    """Immutable pre/post-anchor variance indicator for one (visit, point) series."""

    variance_before: Optional[float]  # None when before_segment < 2 non-NaN values
    variance_after: Optional[float]   # None when after_segment  < 2 non-NaN values
    variance_ratio: Optional[float]   # variance_after / variance_before; None when either is None or before==0


VarianceIndicators = Dict[Tuple[str, str], Optional[VarianceIndicator]]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_variance_indicators(
    sequences: Sequences,
    trigger_results: TriggerResults,
    descent_windows: DescentWindows,
) -> VarianceIndicators:
    """
    Compute pre/post-anchor sample variance indicators for every (visit, point) series.

    Args:
        sequences:       Full ordered marker sequences from build_sequences().
        trigger_results: Anchor positions from detect_triggers().
        descent_windows: Descent windows from determine_descent_windows().

    Returns:
        VarianceIndicators: mapping (visit_id, point_id) -> VarianceIndicator or None.
        None is returned for series with no_cross_marker_effect=True.
        VarianceIndicator fields are None when the cleaned segment has < 2 points.
    """
    indicators: VarianceIndicators = {}

    for key, result in trigger_results.items():
        if result.no_cross_marker_effect:
            indicators[key] = None
            continue

        anchor_index = result.first_positive_index  # type: ignore[arg-type]

        before_clean = [
            v for v in sequences[key][0:anchor_index]
            if not math.isnan(v)
        ]
        after_clean = [
            v for v in descent_windows[key].window_values  # type: ignore[union-attr]
            if not math.isnan(v)
        ]

        variance_before = statistics.variance(before_clean) if len(before_clean) >= 2 else None
        variance_after  = statistics.variance(after_clean)  if len(after_clean)  >= 2 else None

        if variance_before is not None and variance_after is not None and variance_before > 0:
            variance_ratio: Optional[float] = variance_after / variance_before
        else:
            variance_ratio = None

        indicators[key] = VarianceIndicator(
            variance_before=variance_before,
            variance_after=variance_after,
            variance_ratio=variance_ratio,
        )

    logger.debug(
        "CPM-IA variance indicators | total=%d | with_indicator=%d | none=%d",
        len(indicators),
        sum(1 for v in indicators.values() if v is not None),
        sum(1 for v in indicators.values() if v is None),
    )

    return indicators
