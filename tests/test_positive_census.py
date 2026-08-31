# LINKED-TO: [REQ-CPM-IA-P26.0005]
"""Unit tests for src/positive_census.py — TC-05-001 through TC-05-008."""

import pytest

from src.trigger_detection import TriggerResult
from src.positive_census import PointCensus, compute_census


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pos(marker="M1", index=0, value=350.0):
    """Build a TriggerResult with a detected first positive."""
    return TriggerResult(
        first_positive_marker=marker,
        first_positive_index=index,
        first_positive_value=value,
        no_cross_marker_effect=False,
    )


def _neg():
    """Build a TriggerResult with no cross-marker effect."""
    return TriggerResult(
        first_positive_marker=None,
        first_positive_index=None,
        first_positive_value=None,
        no_cross_marker_effect=True,
    )


# ---------------------------------------------------------------------------
# TC-05-001 — Mixed points: P1 positive, P2 no effect, P3 positive
# ---------------------------------------------------------------------------

def test_tc_05_001_two_positive_one_no_effect() -> None:
    """P1 and P3 have positives; P2 does not."""
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _pos(),
        ("V1", "P2"): _neg(),
        ("V2", "P2"): _neg(),
        ("V1", "P3"): _pos(),
        ("V2", "P3"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 2
    assert census.positive_points == ["P1", "P3"]
    assert census.total_point_count == 3


# ---------------------------------------------------------------------------
# TC-05-002 — No positive across any point
# ---------------------------------------------------------------------------

def test_tc_05_002_no_positives_anywhere() -> None:
    """All (visit, point) entries have no_cross_marker_effect=True."""
    results = {
        ("V1", "P1"): _neg(),
        ("V1", "P2"): _neg(),
        ("V2", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 2


# ---------------------------------------------------------------------------
# TC-05-003 — Single (visit, point) with positive
# ---------------------------------------------------------------------------

def test_tc_05_003_single_pair_positive() -> None:
    """Single (visit, point) with a positive: count=1, total=1."""
    census = compute_census({("V1", "P1"): _pos()})
    assert census.positive_point_count == 1
    assert census.positive_points == ["P1"]
    assert census.total_point_count == 1


def test_tc_05_003_single_pair_no_effect() -> None:
    """Single (visit, point) with no effect: count=0, total=1."""
    census = compute_census({("V1", "P1"): _neg()})
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 1


# ---------------------------------------------------------------------------
# TC-05-004 — Empty trigger_results returns zero census
# ---------------------------------------------------------------------------

def test_tc_05_004_empty_returns_zero_census() -> None:
    """Empty input returns PointCensus(0, [], 0) without error."""
    census = compute_census({})
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 0


# ---------------------------------------------------------------------------
# TC-05-005 — Point with mixed visits (one positive, one no-effect) is positive
# ---------------------------------------------------------------------------

def test_tc_05_005_mixed_visits_point_counted_positive() -> None:
    """P1: V1=positive, V2=no-effect → P1 is still a positive point."""
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 1
    assert "P1" in census.positive_points
    assert census.total_point_count == 1


# ---------------------------------------------------------------------------
# TC-05-006 — positive_points is lexicographically sorted
# ---------------------------------------------------------------------------

def test_tc_05_006_positive_points_sorted_lexicographically() -> None:
    """positive_points list must be sorted, not in insertion or discovery order."""
    results = {
        ("V1", "P10"): _pos(),
        ("V1", "P2"):  _pos(),
        ("V1", "P01"): _pos(),
    }
    census = compute_census(results)
    assert census.positive_points == sorted(census.positive_points)
    assert census.positive_points == ["P01", "P10", "P2"]


# ---------------------------------------------------------------------------
# TC-05-007 — total_point_count counts unique points, not (visit, point) pairs
# ---------------------------------------------------------------------------

def test_tc_05_007_total_counts_unique_points_not_pairs() -> None:
    """3 (visit, point) pairs sharing 2 unique points → total_point_count=2."""
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _pos(),
        ("V1", "P2"): _neg(),
    }
    census = compute_census(results)
    assert census.total_point_count == 2   # P1 and P2, not 3 pairs


def test_tc_05_007_positive_count_also_unique() -> None:
    """P1 appears in 3 visits; positive_point_count is 1, not 3."""
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _pos(),
        ("V3", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 1


# ---------------------------------------------------------------------------
# TC-05-008 — PointCensus is immutable
# ---------------------------------------------------------------------------

def test_tc_05_008_point_census_is_immutable() -> None:
    """PointCensus is a frozen dataclass; field assignment must raise."""
    census = compute_census({("V1", "P1"): _pos()})
    with pytest.raises(Exception):
        census.positive_point_count = 99  # type: ignore[misc]
