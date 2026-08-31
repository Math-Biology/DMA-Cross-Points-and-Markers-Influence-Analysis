# LINKED-TO: [REQ-CPM-IA-P26.0006]
"""Unit tests for src/descent_window.py — TC-06-001 through TC-06-012."""

import math

import pytest

from src.trigger_detection import TriggerResult
from src.descent_window import DescentError, DescentWindow, determine_descent_windows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pos(index: int, value: float = 300.0) -> TriggerResult:
    return TriggerResult(
        first_positive_marker=f"M{index}",
        first_positive_index=index,
        first_positive_value=value,
        no_cross_marker_effect=False,
    )


def _neg() -> TriggerResult:
    return TriggerResult(
        first_positive_marker=None,
        first_positive_index=None,
        first_positive_value=None,
        no_cross_marker_effect=True,
    )


def _run(seq, anchor_index=0, epsilon=5.0, n_max=10):
    """Run determine_descent_windows on a single (V1, P1) series."""
    sequences = {("V1", "P1"): seq}
    trigger_results = {("V1", "P1"): _pos(anchor_index, seq[anchor_index])}
    windows = determine_descent_windows(sequences, trigger_results, epsilon, n_max)
    return windows[("V1", "P1")]


# ---------------------------------------------------------------------------
# TC-06-001 — Standard descent closed by a significant rise
# ---------------------------------------------------------------------------

def test_tc_06_001_window_closed_by_rise() -> None:
    """[300,250,200,300] anchor=0 epsilon=5 → window=[300,250,200], truncated=False."""
    w = _run([300.0, 250.0, 200.0, 300.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False


def test_tc_06_001_rise_exactly_at_epsilon_is_not_significant() -> None:
    """Rise == epsilon (val - prev == epsilon) does NOT close the window."""
    # [300, 250, 255] with epsilon=5: 255-250=5 <= 5 → NOT a significant rise
    w = _run([300.0, 250.0, 255.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 255.0]


def test_tc_06_001_rise_just_above_epsilon_closes() -> None:
    """Rise just above epsilon (5.001 > 5.0) closes the window."""
    w = _run([300.0, 250.0, 255.001], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0]
    assert w.window_length == 2


# ---------------------------------------------------------------------------
# TC-06-002 — Monotone descent truncated by n_max (G-07)
# ---------------------------------------------------------------------------

def test_tc_06_002_truncated_by_n_max() -> None:
    """[300,280,260,240,220] n_max=3 → window=[300,280,260], truncated=True."""
    w = _run([300.0, 280.0, 260.0, 240.0, 220.0], anchor_index=0, epsilon=5.0, n_max=3)
    assert w.window_values == [300.0, 280.0, 260.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is True


def test_tc_06_002_natural_end_before_n_max_not_flagged() -> None:
    """Window ends naturally (sequence exhausted) before n_max — truncated=False."""
    w = _run([300.0, 250.0, 200.0], anchor_index=0, epsilon=5.0, n_max=10)
    assert w.truncated_by_n_max is False
    assert w.window_length == 3


def test_tc_06_002_rise_before_n_max_not_flagged() -> None:
    """Window closed by rise before reaching n_max — truncated=False."""
    w = _run([300.0, 250.0, 400.0, 150.0], anchor_index=0, epsilon=5.0, n_max=10)
    assert w.window_values == [300.0, 250.0]
    assert w.truncated_by_n_max is False


# ---------------------------------------------------------------------------
# TC-06-003 — Anchor is last element → single-point window
# ---------------------------------------------------------------------------

def test_tc_06_003_anchor_is_last_element() -> None:
    """Anchor at last index: window has only the anchor, truncated=False."""
    w = _run([100.0, 200.0, 350.0], anchor_index=2, epsilon=5.0)
    assert w.window_values == [350.0]
    assert w.window_length == 1
    assert w.truncated_by_n_max is False


# ---------------------------------------------------------------------------
# TC-06-004 — Rise at first step after anchor → single-point window
# ---------------------------------------------------------------------------

def test_tc_06_004_immediate_rise_gives_single_point_window() -> None:
    """Value immediately after anchor rises beyond epsilon → window=[anchor]."""
    w = _run([300.0, 500.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0]
    assert w.window_length == 1
    assert w.truncated_by_n_max is False


# ---------------------------------------------------------------------------
# TC-06-005 — no_cross_marker_effect=True → None in descent_windows
# ---------------------------------------------------------------------------

def test_tc_06_005_no_effect_series_maps_to_none() -> None:
    """Series with no_cross_marker_effect=True gets None in descent_windows."""
    sequences = {("V1", "P1"): [100.0, 200.0, 250.0]}
    trigger_results = {("V1", "P1"): _neg()}
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)
    assert windows[("V1", "P1")] is None


# ---------------------------------------------------------------------------
# TC-06-006 — n_max < 1 raises DescentError
# ---------------------------------------------------------------------------

def test_tc_06_006_n_max_zero_raises() -> None:
    """n_max=0 raises DescentError before any processing."""
    with pytest.raises(DescentError, match="n_max must be >= 1"):
        determine_descent_windows({}, {}, 5.0, 0)


def test_tc_06_006_n_max_negative_raises() -> None:
    """n_max=-1 raises DescentError."""
    with pytest.raises(DescentError):
        determine_descent_windows({}, {}, 5.0, -1)


# ---------------------------------------------------------------------------
# TC-06-007 — rise_tolerance_epsilon < 0 raises DescentError
# ---------------------------------------------------------------------------

def test_tc_06_007_negative_epsilon_raises() -> None:
    """rise_tolerance_epsilon=-1.0 raises DescentError."""
    with pytest.raises(DescentError, match="rise_tolerance_epsilon must be >= 0"):
        determine_descent_windows({}, {}, -1.0, 10)


# ---------------------------------------------------------------------------
# TC-06-008 — NaN after anchor is bridged (Decision A)
# ---------------------------------------------------------------------------

def test_tc_06_008_nan_bridged_between_descent_values() -> None:
    """NaN between anchor and descent: skipped, prev unchanged, window correct."""
    w = _run([300.0, float("nan"), 250.0, 200.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False


def test_tc_06_008_nan_does_not_count_toward_n_max() -> None:
    """NaN positions are skipped and do not consume n_max slots."""
    # seq=[300, nan, nan, 250, 200]; n_max=3 — 3 real values should fit
    w = _run(
        [300.0, float("nan"), float("nan"), 250.0, 200.0],
        anchor_index=0,
        epsilon=5.0,
        n_max=3,
    )
    assert w.window_values == [300.0, 250.0, 200.0]
    assert w.window_length == 3
    assert w.truncated_by_n_max is False


def test_tc_06_008_nan_bridging_rise_check_against_last_valid() -> None:
    """After NaN, rise comparison uses last valid value before the gap."""
    # [300, nan, 400]: 400-300=100 > epsilon=5 → window=[300] despite NaN
    w = _run([300.0, float("nan"), 400.0], anchor_index=0, epsilon=5.0)
    assert w.window_values == [300.0]
    assert w.window_length == 1


# ---------------------------------------------------------------------------
# TC-06-009 — Anchor mid-sequence
# ---------------------------------------------------------------------------

def test_tc_06_009_anchor_mid_sequence_ignores_pre_anchor_values() -> None:
    """Anchor at index 2; values before index 2 are not part of the window."""
    # seq=[50, 100, 350, 300, 250]; anchor at index 2 (value=350)
    w = _run([50.0, 100.0, 350.0, 300.0, 250.0], anchor_index=2, epsilon=5.0)
    assert w.window_values[0] == 350.0   # window starts at anchor
    assert 50.0 not in w.window_values
    assert 100.0 not in w.window_values
    assert w.window_values == [350.0, 300.0, 250.0]


# ---------------------------------------------------------------------------
# TC-06-010 — epsilon=0: equal step is NOT a rise (appended)
# ---------------------------------------------------------------------------

def test_tc_06_010_equal_step_with_epsilon_zero_is_not_a_rise() -> None:
    """val - prev == 0 <= 0 (epsilon=0): flat step is appended (strictly non-increasing)."""
    w = _run([300.0, 300.0, 250.0], anchor_index=0, epsilon=0.0)
    assert w.window_values == [300.0, 300.0, 250.0]


def test_tc_06_010_any_positive_step_with_epsilon_zero_closes() -> None:
    """val - prev = 0.001 > 0 (epsilon=0): tiniest rise closes window."""
    w = _run([300.0, 300.001], anchor_index=0, epsilon=0.0)
    assert w.window_values == [300.0]


# ---------------------------------------------------------------------------
# TC-06-011 — n_max=1: window always only the anchor (Decision B)
# ---------------------------------------------------------------------------

def test_tc_06_011_n_max_1_window_is_anchor_only() -> None:
    """n_max=1: next non-rising value would be appended but cap fires → truncated=True."""
    w = _run([300.0, 250.0], anchor_index=0, epsilon=5.0, n_max=1)
    assert w.window_values == [300.0]
    assert w.window_length == 1
    assert w.truncated_by_n_max is True


def test_tc_06_011_n_max_1_anchor_is_last_element_not_truncated() -> None:
    """n_max=1 but anchor is already last element: nothing to truncate → truncated=False."""
    w = _run([100.0, 300.0], anchor_index=1, epsilon=5.0, n_max=1)
    assert w.window_values == [300.0]
    assert w.truncated_by_n_max is False


# ---------------------------------------------------------------------------
# TC-06-012 — Multiple (v,p) pairs with mixed anchors and no-effects
# ---------------------------------------------------------------------------

def test_tc_06_012_multiple_pairs_independent_results() -> None:
    """Each (visit, point) pair is processed independently."""
    sequences = {
        ("V1", "P1"): [300.0, 250.0, 200.0, 400.0],  # window=[300,250,200]
        ("V1", "P2"): [100.0, 200.0, 150.0],          # no_effect
        ("V2", "P1"): [50.0, 400.0, 350.0, 300.0],    # anchor at idx 1
    }
    trigger_results = {
        ("V1", "P1"): _pos(0, 300.0),
        ("V1", "P2"): _neg(),
        ("V2", "P1"): _pos(1, 400.0),
    }
    windows = determine_descent_windows(sequences, trigger_results, 5.0, 10)

    assert windows[("V1", "P1")].window_values == [300.0, 250.0, 200.0]
    assert windows[("V1", "P2")] is None
    assert windows[("V2", "P1")].window_values == [400.0, 350.0, 300.0]
    assert windows[("V2", "P1")].truncated_by_n_max is False
