# LINKED-TO: [REQ-CPM-IA-P26.0005]
"""
positive_census.py — Positive Census Across Points for the CPM-IA component.

Aggregates per-(visit, point) trigger results to the anatomical-point level,
counting and identifying unique points that have at least one positive anchor
across any visit. Produced census is consumed by Module 10 (output consolidation).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from src.trigger_detection import TriggerResults

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PointCensus:
    """Immutable census of anatomical points showing cross-marker excitation."""

    positive_point_count: int        # number of points with at least one positive
    positive_points: List[str]       # sorted identifiers of those points
    total_point_count: int           # total unique anatomical points in the dataset
    total_positives_count: int       # sum of positives_count across all positive series


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_census(trigger_results: TriggerResults) -> PointCensus:
    """
    Aggregate trigger results to anatomical-point level.

    A point is positive when at least one (visit, point) entry has
    no_cross_marker_effect = False. Empty input returns a zero census.

    Args:
        trigger_results: Mapping (visit_id, point_id) -> TriggerResult from detect_triggers().

    Returns:
        PointCensus with positive_point_count, positive_points (sorted),
        total_point_count, total_positives_count.
    """
    if not trigger_results:
        return PointCensus(
            positive_point_count=0,
            positive_points=[],
            total_point_count=0,
            total_positives_count=0,
        )

    # All unique anatomical points across the dataset
    all_points = {point for (_, point) in trigger_results}

    # Points that have at least one visit with a detected positive.
    # sorted() is intentional and spec-mandated here for deterministic output —
    # contrast with G-04 (Module 03) where sorting was forbidden for marker order.
    positive_set = {
        point
        for (_, point), result in trigger_results.items()
        if not result.no_cross_marker_effect
    }
    positive_points = sorted(positive_set)

    # Total anchor count across all series
    total_positives_count = sum(
        result.positives_count for result in trigger_results.values()
    )

    census = PointCensus(
        positive_point_count=len(positive_points),
        positive_points=positive_points,
        total_point_count=len(all_points),
        total_positives_count=total_positives_count,
    )

    logger.info(
        "CPM-IA census | positive_points=%d/%d | total_anchors=%d | points=%s",
        census.positive_point_count,
        census.total_point_count,
        census.total_positives_count,
        census.positive_points,
    )

    return census
