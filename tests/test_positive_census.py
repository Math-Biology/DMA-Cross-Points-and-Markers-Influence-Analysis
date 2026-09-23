# LINKED-TO: [REQ-CPM-IA-P26.0005]
"""Unit tests for src/positive_census.py — TC-05-001 through TC-05-009."""

import pytest

from src.trigger_detection import Anchor, TriggerResult
from src.positive_census import PointCensus, compute_census


def _pos(marker="M1", index=0, value=350.0):
    anchor = Anchor(marker=marker, index=index, value=value)
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


def _pos_multi(positives_count=2):
    anchors = [Anchor(marker=f"M{i}", index=i, value=350.0) for i in range(positives_count)]
    return TriggerResult(anchors=anchors, positives_count=positives_count, no_cross_marker_effect=False)


def _neg():
    return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)


def test_tc_05_001_two_positive_one_no_effect():
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


def test_tc_05_002_no_positives_anywhere():
    results = {
        ("V1", "P1"): _neg(),
        ("V1", "P2"): _neg(),
        ("V2", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 2


def test_tc_05_003_single_pair_positive():
    census = compute_census({("V1", "P1"): _pos()})
    assert census.positive_point_count == 1
    assert census.positive_points == ["P1"]
    assert census.total_point_count == 1


def test_tc_05_003_single_pair_no_effect():
    census = compute_census({("V1", "P1"): _neg()})
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 1


def test_tc_05_004_empty_returns_zero_census():
    census = compute_census({})
    assert census.positive_point_count == 0
    assert census.positive_points == []
    assert census.total_point_count == 0
    assert census.total_positives_count == 0


def test_tc_05_005_mixed_visits_point_counted_positive():
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 1
    assert "P1" in census.positive_points
    assert census.total_point_count == 1


def test_tc_05_006_positive_points_sorted_lexicographically():
    results = {
        ("V1", "P10"): _pos(),
        ("V1", "P2"):  _pos(),
        ("V1", "P01"): _pos(),
    }
    census = compute_census(results)
    assert census.positive_points == sorted(census.positive_points)
    assert census.positive_points == ["P01", "P10", "P2"]


def test_tc_05_007_total_counts_unique_points_not_pairs():
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _pos(),
        ("V1", "P2"): _neg(),
    }
    census = compute_census(results)
    assert census.total_point_count == 2


def test_tc_05_007_positive_count_also_unique():
    results = {
        ("V1", "P1"): _pos(),
        ("V2", "P1"): _pos(),
        ("V3", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.positive_point_count == 1


def test_tc_05_008_point_census_is_immutable():
    census = compute_census({("V1", "P1"): _pos()})
    with pytest.raises(Exception):
        census.positive_point_count = 99  # type: ignore[misc]


def test_tc_05_009_total_positives_count_single():
    census = compute_census({("V1", "P1"): _pos()})
    assert census.total_positives_count == 1


def test_tc_05_009_total_positives_count_multi():
    results = {
        ("V1", "P1"): _pos_multi(2),
        ("V1", "P2"): _pos_multi(3),
        ("V2", "P1"): _neg(),
    }
    census = compute_census(results)
    assert census.total_positives_count == 5


def test_tc_05_009_total_positives_count_zero_for_no_effect():
    results = {("V1", "P1"): _neg(), ("V2", "P1"): _neg()}
    census = compute_census(results)
    assert census.total_positives_count == 0
