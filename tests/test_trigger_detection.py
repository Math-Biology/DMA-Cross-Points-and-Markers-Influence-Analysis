# LINKED-TO: [REQ-CPM-IA-P26.0004]
"""Unit tests for src/trigger_detection.py — TC-04-001 through TC-04-015."""

import math
import pytest

from src.trigger_detection import Anchor, TriggerError, TriggerResult, detect_triggers


def _run(values_per_pair, marker_orders, threshold=300.0):
    sequences = {k: v for k, v in values_per_pair.items()}
    return detect_triggers(sequences, marker_orders, threshold)


def _single(values, markers=None, threshold=300.0):
    if markers is None:
        markers = [f"M{i}" for i in range(len(values))]
    result = _run({("V1", "P1"): values}, {"V1": markers}, threshold)
    return result[("V1", "P1")]


# ---------------------------------------------------------------------------
# TC-04-001 — Second marker is the first positive (>= threshold now)
# ---------------------------------------------------------------------------

def test_tc_04_001_first_positive_is_second_marker():
    r = _single([100.0, 350.0, 400.0], ["M1", "M2", "M3"])
    assert r.anchors[0].marker == "M2"
    assert r.anchors[0].index == 1
    assert r.anchors[0].value == 350.0
    assert r.no_cross_marker_effect is False


# ---------------------------------------------------------------------------
# TC-04-002 — No marker meets threshold
# ---------------------------------------------------------------------------

def test_tc_04_002_no_positive_flags_no_effect():
    r = _single([100.0, 200.0, 250.0], ["M1", "M2", "M3"])
    assert r.no_cross_marker_effect is True
    assert r.anchors == []
    assert r.positives_count == 0


# ---------------------------------------------------------------------------
# TC-04-003 — All positives collected (no break after first)
# ---------------------------------------------------------------------------

def test_tc_04_003_all_positives_collected():
    """M1=400, M2=500 both exceed threshold → 2 anchors."""
    r = _single([400.0, 500.0], ["M1", "M2"])
    assert len(r.anchors) == 2
    assert r.anchors[0].marker == "M1"
    assert r.anchors[1].marker == "M2"
    assert r.positives_count == 2
    assert r.no_cross_marker_effect is False


def test_tc_04_003_three_positives():
    r = _single([301.0, 400.0, 500.0], ["M1", "M2", "M3"])
    assert len(r.anchors) == 3
    assert r.positives_count == 3


def test_tc_04_003_anchor_order_matches_sequence():
    r = _single([100.0, 350.0, 200.0, 400.0], ["M1", "M2", "M3", "M4"])
    assert len(r.anchors) == 2
    assert r.anchors[0].marker == "M2"
    assert r.anchors[1].marker == "M4"


# ---------------------------------------------------------------------------
# TC-04-004 — All NaN → no positive
# ---------------------------------------------------------------------------

def test_tc_04_004_all_nan_gives_no_effect():
    r = _single([float("nan"), float("nan"), float("nan")], ["M1", "M2", "M3"])
    assert r.no_cross_marker_effect is True
    assert r.anchors == []


# ---------------------------------------------------------------------------
# TC-04-005 — threshold_pct = 0 raises TriggerError
# ---------------------------------------------------------------------------

def test_tc_04_005_threshold_zero_raises():
    with pytest.raises(TriggerError, match="threshold_pct must be positive"):
        _single([100.0], threshold=0.0)


# ---------------------------------------------------------------------------
# TC-04-006 — Value exactly equals threshold IS a positive (>= inclusive)
# ---------------------------------------------------------------------------

def test_tc_04_006_exact_threshold_is_positive():
    """value == threshold_pct (300.0 == 300.0) NOW IS a positive (>= inclusive)."""
    r = _single([300.0, 250.0], ["M1", "M2"], threshold=300.0)
    assert r.no_cross_marker_effect is False
    assert len(r.anchors) == 1
    assert r.anchors[0].marker == "M1"
    assert r.anchors[0].value == 300.0


def test_tc_04_006_just_below_threshold_not_positive():
    """value = 299.999 < 300.0 must NOT trigger a positive."""
    r = _single([299.999], ["M1"], threshold=300.0)
    assert r.no_cross_marker_effect is True


def test_tc_04_006_one_above_threshold_is_positive():
    r = _single([300.001], ["M1"], threshold=300.0)
    assert r.no_cross_marker_effect is False
    assert r.anchors[0].marker == "M1"


# ---------------------------------------------------------------------------
# TC-04-007 — threshold_pct < 0 raises TriggerError
# ---------------------------------------------------------------------------

def test_tc_04_007_negative_threshold_raises():
    with pytest.raises(TriggerError):
        _single([100.0], threshold=-1.0)


# ---------------------------------------------------------------------------
# TC-04-008 — NaN before the first positive is skipped
# ---------------------------------------------------------------------------

def test_tc_04_008_nan_before_positive_is_skipped():
    r = _single([float("nan"), 350.0, 200.0], ["M1", "M2", "M3"])
    assert r.anchors[0].marker == "M2"
    assert r.anchors[0].index == 1
    assert r.anchors[0].value == 350.0


def test_tc_04_008_nan_interspersed():
    r = _single([float("nan"), float("nan"), 400.0], ["M1", "M2", "M3"])
    assert r.anchors[0].marker == "M3"
    assert r.anchors[0].index == 2


# ---------------------------------------------------------------------------
# TC-04-009 — Empty sequences dict returns empty dict
# ---------------------------------------------------------------------------

def test_tc_04_009_empty_sequences_returns_empty():
    result = detect_triggers({}, {}, 300.0)
    assert result == {}


# ---------------------------------------------------------------------------
# TC-04-010 — Multiple (visit, point) pairs with mixed outcomes
# ---------------------------------------------------------------------------

def test_tc_04_010_mixed_outcomes_across_pairs():
    sequences = {
        ("V1", "P1"): [100.0, 350.0, 200.0],   # positive at M2
        ("V1", "P2"): [50.0, 100.0, 200.0],     # no positive
        ("V2", "P1"): [400.0, 500.0, 600.0],    # all positive
    }
    markers = ["M1", "M2", "M3"]
    results = detect_triggers(sequences, {"V1": markers, "V2": markers}, 300.0)

    assert results[("V1", "P1")].anchors[0].marker == "M2"
    assert results[("V1", "P1")].no_cross_marker_effect is False

    assert results[("V1", "P2")].no_cross_marker_effect is True
    assert results[("V1", "P2")].anchors == []

    assert results[("V2", "P1")].positives_count == 3


# ---------------------------------------------------------------------------
# TC-04-011 — TriggerResult is immutable
# ---------------------------------------------------------------------------

def test_tc_04_011_trigger_result_is_immutable():
    r = _single([400.0], ["M1"])
    with pytest.raises(Exception):
        r.anchors = []  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TC-04-012 — Anchor dataclass fields
# ---------------------------------------------------------------------------

def test_tc_04_012_anchor_fields():
    r = _single([100.0, 350.0, 400.0], ["M1", "M2", "M3"])
    a = r.anchors[0]
    assert isinstance(a, Anchor)
    assert a.marker == "M2"
    assert a.index == 1
    assert a.value == 350.0


def test_tc_04_012_anchor_is_immutable():
    r = _single([400.0], ["M1"])
    with pytest.raises(Exception):
        r.anchors[0].marker = "X"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TC-04-013 — NaN values are skipped when collecting all positives
# ---------------------------------------------------------------------------

def test_tc_04_013_nan_skipped_collecting_all():
    """NaN in the middle: both non-NaN positives are collected."""
    r = _single([350.0, float("nan"), 400.0], ["M1", "M2", "M3"])
    assert len(r.anchors) == 2
    assert r.anchors[0].marker == "M1"
    assert r.anchors[1].marker == "M3"
    assert r.anchors[1].index == 2


# ---------------------------------------------------------------------------
# TC-04-014 — Consecutive peaks: anchor_run_lengths and max_consecutive_peaks
# ---------------------------------------------------------------------------

def _anchors_at(indices, values=None):
    """Build a list of Anchors at the given sequence indices."""
    from src.trigger_detection import Anchor
    if values is None:
        values = [400.0] * len(indices)
    return [Anchor(marker=f"M{idx}", index=idx, value=v) for idx, v in zip(indices, values)]


def test_tc_04_014_no_anchors():
    """No anchors -> anchor_run_lengths=[], max_consecutive_peaks=0."""
    r = _single([], [])
    assert r.anchor_run_lengths == []
    assert r.consecutive_peaks == 0


def test_tc_04_014_single_isolated_anchor():
    """One anchor at index 2 (isolated) -> run_length=[1], max=1."""
    r = _single([100.0, 200.0, 400.0], ["M1", "M2", "M3"])
    assert r.anchor_run_lengths == [1]
    assert r.consecutive_peaks == 0


def test_tc_04_014_two_consecutive_anchors():
    """Anchors at indices 0,1 (consecutive) -> run_lengths=[2,2], max=2."""
    r = _single([400.0, 400.0, 100.0], ["M1", "M2", "M3"])
    assert r.anchor_run_lengths == [2, 2]
    assert r.consecutive_peaks == 2


def test_tc_04_014_three_consecutive_anchors():
    """Anchors at indices 0,1,2 (consecutive) -> run_lengths=[3,3,3], max=3."""
    r = _single([400.0, 400.0, 400.0], ["M1", "M2", "M3"])
    assert r.anchor_run_lengths == [3, 3, 3]
    assert r.consecutive_peaks == 3


def test_tc_04_014_non_consecutive_anchors():
    """Anchors at indices 0 and 2 (gap at 1) -> run_lengths=[1,1], max=1."""
    r = _single([400.0, 100.0, 400.0], ["M1", "M2", "M3"])
    assert r.anchor_run_lengths == [1, 1]
    assert r.consecutive_peaks == 0


def test_tc_04_014_mixed_run_leading_pair():
    """Anchors at indices 0,1,3 -> runs: [2,2] then [1] -> run_lengths=[2,2,1], max=2."""
    r = _single([400.0, 400.0, 100.0, 400.0], ["M1", "M2", "M3", "M4"])
    assert r.anchor_run_lengths == [2, 2, 1]
    assert r.consecutive_peaks == 2


def test_tc_04_014_mixed_run_trailing_pair():
    """Anchors at indices 0,2,3 -> runs: [1] then [2,2] -> run_lengths=[1,2,2], max=2."""
    r = _single([400.0, 100.0, 400.0, 400.0], ["M1", "M2", "M3", "M4"])
    assert r.anchor_run_lengths == [1, 2, 2]
    assert r.consecutive_peaks == 2
