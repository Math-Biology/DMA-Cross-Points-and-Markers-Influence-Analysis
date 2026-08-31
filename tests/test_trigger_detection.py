# LINKED-TO: [REQ-CPM-IA-P26.0004]
"""Unit tests for src/trigger_detection.py — TC-04-001 through TC-04-011."""

import math

import pytest

from src.trigger_detection import TriggerError, TriggerResult, detect_triggers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(values_per_pair, marker_orders, threshold=300.0):
    """Build sequences dict and call detect_triggers. marker_orders is Dict[str, List[str]]."""
    sequences = {k: v for k, v in values_per_pair.items()}
    return detect_triggers(sequences, marker_orders, threshold)


def _single(values, markers=None, threshold=300.0):
    """Run detection on a single (V1, P1) series. markers defaults to M0..Mn."""
    if markers is None:
        markers = [f"M{i}" for i in range(len(values))]
    result = _run({("V1", "P1"): values}, {"V1": markers}, threshold)
    return result[("V1", "P1")]


# ---------------------------------------------------------------------------
# TC-04-001 — Second marker is the first positive
# ---------------------------------------------------------------------------

def test_tc_04_001_first_positive_is_second_marker() -> None:
    """M1=100, M2=350, M3=400 with threshold=300 → anchor is M2 at index 1."""
    r = _single([100.0, 350.0, 400.0], ["M1", "M2", "M3"])
    assert r.first_positive_marker == "M2"
    assert r.first_positive_index == 1
    assert r.first_positive_value == 350.0
    assert r.no_cross_marker_effect is False


# ---------------------------------------------------------------------------
# TC-04-002 — No marker exceeds threshold
# ---------------------------------------------------------------------------

def test_tc_04_002_no_positive_flags_no_effect() -> None:
    """M1=100, M2=200, M3=250 with threshold=300 → no_cross_marker_effect=True."""
    r = _single([100.0, 200.0, 250.0], ["M1", "M2", "M3"])
    assert r.no_cross_marker_effect is True
    assert r.first_positive_marker is None
    assert r.first_positive_index is None
    assert r.first_positive_value is None


# ---------------------------------------------------------------------------
# TC-04-003 — First marker already exceeds; second must not become anchor (G-05)
# ---------------------------------------------------------------------------

def test_tc_04_003_anchor_is_first_exceedance_only() -> None:
    """M1=400 exceeds threshold; M2=500 must NOT redefine the anchor (G-05)."""
    r = _single([400.0, 500.0], ["M1", "M2"])
    assert r.first_positive_marker == "M1"
    assert r.first_positive_index == 0
    assert r.first_positive_value == 400.0
    assert r.no_cross_marker_effect is False


def test_tc_04_003_only_one_anchor_recorded() -> None:
    """Three markers all exceeding threshold: only the first is the anchor."""
    r = _single([301.0, 400.0, 500.0], ["M1", "M2", "M3"])
    assert r.first_positive_marker == "M1"
    assert r.first_positive_index == 0


# ---------------------------------------------------------------------------
# TC-04-004 — All NaN → no positive
# ---------------------------------------------------------------------------

def test_tc_04_004_all_nan_gives_no_effect() -> None:
    """All-NaN sequence: NaN values are skipped, result is no_cross_marker_effect=True."""
    r = _single([float("nan"), float("nan"), float("nan")], ["M1", "M2", "M3"])
    assert r.no_cross_marker_effect is True
    assert r.first_positive_marker is None


# ---------------------------------------------------------------------------
# TC-04-005 — threshold_pct = 0 raises TriggerError
# ---------------------------------------------------------------------------

def test_tc_04_005_threshold_zero_raises() -> None:
    """threshold_pct=0 raises TriggerError before any processing."""
    with pytest.raises(TriggerError, match="threshold_pct must be positive"):
        _single([100.0], threshold=0.0)


# ---------------------------------------------------------------------------
# TC-04-006 — Value exactly equals threshold is NOT a positive (strict >)
# ---------------------------------------------------------------------------

def test_tc_04_006_exact_threshold_not_positive() -> None:
    """value == threshold_pct (300.0 == 300.0) must NOT trigger a positive."""
    r = _single([300.0, 250.0], ["M1", "M2"], threshold=300.0)
    assert r.no_cross_marker_effect is True


def test_tc_04_006_one_above_threshold_is_positive() -> None:
    """value = 300.001 > 300.0 must trigger a positive."""
    r = _single([300.001], ["M1"], threshold=300.0)
    assert r.no_cross_marker_effect is False
    assert r.first_positive_marker == "M1"


# ---------------------------------------------------------------------------
# TC-04-007 — threshold_pct < 0 raises TriggerError
# ---------------------------------------------------------------------------

def test_tc_04_007_negative_threshold_raises() -> None:
    """Negative threshold raises TriggerError."""
    with pytest.raises(TriggerError):
        _single([100.0], threshold=-1.0)


# ---------------------------------------------------------------------------
# TC-04-008 — NaN before the first positive is skipped
# ---------------------------------------------------------------------------

def test_tc_04_008_nan_before_positive_is_skipped() -> None:
    """NaN at index 0, positive at index 1 → anchor is M2 at index 1."""
    r = _single([float("nan"), 350.0, 200.0], ["M1", "M2", "M3"])
    assert r.first_positive_marker == "M2"
    assert r.first_positive_index == 1
    assert r.first_positive_value == 350.0


def test_tc_04_008_nan_interspersed() -> None:
    """NaN values between markers do not affect anchor selection."""
    r = _single([float("nan"), float("nan"), 400.0], ["M1", "M2", "M3"])
    assert r.first_positive_marker == "M3"
    assert r.first_positive_index == 2


# ---------------------------------------------------------------------------
# TC-04-009 — Empty sequences dict returns empty dict
# ---------------------------------------------------------------------------

def test_tc_04_009_empty_sequences_returns_empty() -> None:
    """Empty input sequences: returns {} without error (Module 03 owns the empty guard)."""
    result = detect_triggers({}, {}, 300.0)
    assert result == {}


# ---------------------------------------------------------------------------
# TC-04-010 — Multiple (visit, point) pairs with mixed outcomes
# ---------------------------------------------------------------------------

def test_tc_04_010_mixed_outcomes_across_pairs() -> None:
    """Each (visit, point) pair is classified independently."""
    sequences = {
        ("V1", "P1"): [100.0, 350.0, 200.0],   # positive at M2
        ("V1", "P2"): [50.0, 100.0, 200.0],     # no positive
        ("V2", "P1"): [400.0, 500.0, 600.0],    # positive at M1
    }
    markers = ["M1", "M2", "M3"]
    results = detect_triggers(sequences, {"V1": markers, "V2": markers}, 300.0)

    assert results[("V1", "P1")].first_positive_marker == "M2"
    assert results[("V1", "P1")].no_cross_marker_effect is False

    assert results[("V1", "P2")].no_cross_marker_effect is True
    assert results[("V1", "P2")].first_positive_marker is None

    assert results[("V2", "P1")].first_positive_marker == "M1"
    assert results[("V2", "P1")].first_positive_index == 0


def test_tc_04_010_all_pairs_present_in_output() -> None:
    """Every input (visit, point) key must appear in trigger_results (G-06)."""
    sequences = {
        ("V1", "P1"): [100.0, 350.0],
        ("V1", "P2"): [50.0, 100.0],
    }
    results = detect_triggers(sequences, {"V1": ["M1", "M2"]}, 300.0)
    assert set(results.keys()) == {("V1", "P1"), ("V1", "P2")}


# ---------------------------------------------------------------------------
# TC-04-011 — TriggerResult is immutable
# ---------------------------------------------------------------------------

def test_tc_04_011_trigger_result_is_immutable() -> None:
    """TriggerResult is a frozen dataclass; field assignment must raise."""
    r = _single([400.0], ["M1"])
    with pytest.raises(Exception):
        r.first_positive_marker = "X"  # type: ignore[misc]
