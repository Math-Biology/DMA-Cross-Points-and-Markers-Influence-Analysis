# LINKED-TO: [REQ-CPM-IA-P26.0006]
"""Unit tests for src/descent_window.py — TC-06-001 through TC-06-015."""

import math
import pytest

from src.trigger_detection import Anchor, TriggerResult
from src.descent_window import DescentError, DescentWindow, determine_descent_windows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result_with_anchors(anchor_indices, seq):
    """Build a TriggerResult with multiple anchors at the given indices."""
    anchors = [Anchor(marker=f"M{i}", index=i, value=seq[i]) for i in anchor_indices]
    return TriggerResult(
        anchors=anchors,
        positives_count=len(anchors),
        no_cross_marker_effect=len(anchors) == 0,
    )


def _neg():
    return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)


def _pos_single(index, seq):
    """Single-anchor TriggerResult."""
    anchor = Anchor(marker=f"M{index}", index=index, value=seq[index])
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


def _run(seq, anchor_index=0, epsilon=5.0, n_max=10):
    """Run determine_descent_windows on a single (V1, P1) series with one anchor."""
    sequences = {("V1", "P1"): seq}
    trigger_results = {("V1", "P1"): _pos_single(anchor_index, seq)}
    windows = determine_descent_windows(sequences, trigger_results, epsilon, n_max)
    wlist = windows[("V1", "P1")]
    assert len(wlist) == 1
    return wlist[0]


# ---------------------------------------------------------------------------
# TC-06-001 — Standard descent closed by a significant rise
# ---------------------------------------------------------------------------

def test_tc_06_001_window_closed_by_rise():
    w = _run([300.0, 250.0, 200.0, 300.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False
    assert w.window_close_reason == "rise"


def test_tc_06_001_rise_exactly_at_epsilon_is_not_significant():
    w = _run([300.0, 250.0, 255.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 255.0]
    assert w.window_close_reason == "end"


def test_tc_06_001_rise_just_above_epsilon_closes():
    w = _run([300.0, 250.0, 255.001], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0]
    assert w.window_length == 2
    assert w.window_close_reason == "rise"


# ---------------------------------------------------------------------------
# TC-06-002 — Monotone descent truncated by n_max (G-07)
# ---------------------------------------------------------------------------

def test_tc_06_002_truncated_by_n_max():
    w = _run([300.0, 280.0, 260.0, 240.0, 220.0], anchor_index=0, epsilon=5.0, n_max=3)
    assert w.window_values == [300.0, 280.0, 260.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is True
    assert w.window_close_reason == "n_max"


def test_tc_06_002_natural_end_before_n_max_not_flagged():
    w = _run([300.0, 250.0, 200.0], anchor_index=0, epsilon=5.0, n_max=10)
    assert w.truncated_by_n_max is False
    assert w.window_length == 3
    assert w.window_close_reason == "end"


# ---------------------------------------------------------------------------
# TC-06-003 — Anchor is last element → single-point window
# ---------------------------------------------------------------------------

def test_tc_06_003_anchor_is_last_element():
    w = _run([100.0, 200.0, 350.0], anchor_index=2, epsilon=5.0)
    assert w.window_values == [350.0]
    assert w.window_length == 1
    assert w.truncated_by_n_max is False
    assert w.window_close_reason == "end"


# ---------------------------------------------------------------------------
# TC-06-004 — Rise at first step after anchor → single-point window
# ---------------------------------------------------------------------------

def test_tc_06_004_immediate_rise_gives_single_point_window():
    w = _run([300.0, 500.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0]
    assert w.window_length == 1
    assert w.window_close_reason == "rise"


# ---------------------------------------------------------------------------
# TC-06-005 — no_cross_marker_effect=True → empty list in descent_windows
# ---------------------------------------------------------------------------

def test_tc_06_005_no_effect_series_maps_to_empty_list():
    sequences = {("V1", "P1"): [100.0, 200.0, 250.0]}
    trigger_results = {("V1", "P1"): _neg()}
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)
    assert windows[("V1", "P1")] == []


# ---------------------------------------------------------------------------
# TC-06-006 — n_max < 1 raises DescentError
# ---------------------------------------------------------------------------

def test_tc_06_006_n_max_zero_raises():
    with pytest.raises(DescentError, match="n_max must be >= 1"):
        determine_descent_windows({}, {}, 5.0, 0)


def test_tc_06_006_n_max_negative_raises():
    with pytest.raises(DescentError):
        determine_descent_windows({}, {}, 5.0, -1)


# ---------------------------------------------------------------------------
# TC-06-007 — rise_tolerance_epsilon < 0 raises DescentError
# ---------------------------------------------------------------------------

def test_tc_06_007_negative_epsilon_raises():
    with pytest.raises(DescentError, match="rise_tolerance_epsilon must be >= 0"):
        determine_descent_windows({}, {}, -1.0, 10)


# ---------------------------------------------------------------------------
# TC-06-008 — NaN after anchor is bridged (Decision A)
# ---------------------------------------------------------------------------

def test_tc_06_008_nan_bridged_between_descent_values():
    w = _run([300.0, float("nan"), 250.0, 200.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False


def test_tc_06_008_nan_does_not_count_toward_n_max():
    w = _run(
        [300.0, float("nan"), float("nan"), 250.0, 200.0],
        anchor_index=0, epsilon=5.0, n_max=3,
    )
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False


def test_tc_06_008_nan_bridging_rise_check_against_last_valid():
    w = _run([300.0, float("nan"), 400.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0]
    assert w.window_length == 1
    assert w.window_close_reason == "rise"


# ---------------------------------------------------------------------------
# TC-06-009 — Anchor mid-sequence
# ---------------------------------------------------------------------------

def test_tc_06_009_anchor_mid_sequence_ignores_pre_anchor_values():
    w = _run([50.0, 100.0, 350.0, 300.0, 250.0], anchor_index=2, epsilon=5.0)
    assert w.window_values[0] == 350.0
    assert 50.0 not in w.window_values
    assert w.window_values == [350.0, 300.0, 250.0]


# ---------------------------------------------------------------------------
# TC-06-010 — epsilon=0 behaviour
# ---------------------------------------------------------------------------

def test_tc_06_010_equal_step_with_epsilon_zero_is_not_a_rise():
    w = _run([300.0, 300.0, 250.0], anchor_index=0, epsilon=0.0)
    assert w.window_values == [300.0, 300.0, 250.0]


def test_tc_06_010_any_positive_step_with_epsilon_zero_closes():
    w = _run([300.0, 300.001], anchor_index=0, epsilon=0.0)
    assert w.window_values == [300.0]
    assert w.window_close_reason == "rise"


# ---------------------------------------------------------------------------
# TC-06-011 — n_max=1: window always only the anchor
# ---------------------------------------------------------------------------

def test_tc_06_011_n_max_1_window_is_anchor_only():
    w = _run([300.0, 250.0], anchor_index=0, epsilon=5.0, n_max=1)
    assert w.window_values == [300.0]
    assert w.window_length == 1
    assert w.truncated_by_n_max is True
    assert w.window_close_reason == "n_max"


def test_tc_06_011_n_max_1_anchor_is_last_element_not_truncated():
    w = _run([100.0, 300.0], anchor_index=1, epsilon=5.0, n_max=1)
    assert w.window_values == [300.0]
    assert w.truncated_by_n_max is False


# ---------------------------------------------------------------------------
# TC-06-012 — Multiple (v,p) pairs with mixed anchors and no-effects
# ---------------------------------------------------------------------------

def test_tc_06_012_multiple_pairs_independent_results():
    sequences = {
        ("V1", "P1"): [300.0, 250.0, 200.0, 400.0],
        ("V1", "P2"): [100.0, 200.0, 150.0],
        ("V2", "P1"): [50.0, 400.0, 350.0, 300.0],
    }
    trigger_results = {
        ("V1", "P1"): _pos_single(0, sequences[("V1", "P1")]),
        ("V1", "P2"): _neg(),
        ("V2", "P1"): _pos_single(1, sequences[("V2", "P1")]),
    }
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)

    assert windows[("V1", "P1")][0].window_values == [300.0, 250.0, 200.0]
    assert windows[("V1", "P2")] == []
    assert windows[("V2", "P1")][0].window_values == [400.0, 350.0, 300.0]


# ---------------------------------------------------------------------------
# TC-06-013 — Two anchors in same series → two windows, second closes at next_positive
# ---------------------------------------------------------------------------

def test_tc_06_013_two_anchors_two_windows():
    """Series [300, 250, 400, 350] with anchors at idx=0 and idx=2."""
    seq = [300.0, 250.0, 400.0, 350.0]
    result = _make_result_with_anchors([0, 2], seq)
    sequences = {("V1", "P1"): seq}
    trigger_results = {("V1", "P1"): result}
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)

    wlist = windows[("V1", "P1")]
    assert len(wlist) == 2

    # First window: starts at idx=0 (300.0), closes at next_positive (idx=2)
    assert wlist[0].window_values == [300.0, 250.0]
    assert wlist[0].window_close_reason == "next_positive"

    # Second window: starts at idx=2 (400.0), descends to 350.0
    assert wlist[1].window_values[0] == 400.0
    assert wlist[1].window_values == [400.0, 350.0]


def test_tc_06_013_adjacent_anchors():
    """Adjacent anchors at idx 0 and 1 → first window is single-point (next_positive closes)."""
    seq = [300.0, 400.0, 350.0]
    result = _make_result_with_anchors([0, 1], seq)
    sequences = {("V1", "P1"): seq}
    trigger_results = {("V1", "P1"): result}
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)
    wlist = windows[("V1", "P1")]
    assert len(wlist) == 2
    assert wlist[0].window_values == [300.0]
    assert wlist[0].window_close_reason == "next_positive"


# ---------------------------------------------------------------------------
# TC-06-014 — window_close_reason field present on all windows
# ---------------------------------------------------------------------------

def test_tc_06_014_window_close_reason_field_exists():
    w = _run([300.0, 250.0, 200.0], anchor_index=0, epsilon=5.0)
    assert hasattr(w, "window_close_reason")
    assert w.window_close_reason in ("rise", "next_positive", "n_max", "end")
