# LINKED-TO: [REQ-CPM-IA-P26.0007]
"""
Unit tests for src/descent_slope.py — Module 07: Descent Slope Computation.
"""

import logging
import math

import numpy as np
import pytest

from src.descent_window import DescentWindow
from src.descent_slope import SlopeError, _ols_slope, compute_slopes


def _make_window(values, truncated=False, close_reason="end"):
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
        window_close_reason=close_reason,
    )


def _polyfit_slope(values):
    n = len(values)
    x = list(range(n))
    return float(np.polyfit(x, values, 1)[0])


class TestTC07001:
    def test_slope_value(self):
        assert _ols_slope([300.0, 200.0, 100.0]) == pytest.approx(-100.0)

    def test_matches_polyfit(self):
        values = [300.0, 200.0, 100.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values))


class TestTC07002:
    def test_slope_value(self):
        assert _ols_slope([300.0, 250.0]) == pytest.approx(-50.0)

    def test_matches_polyfit(self):
        values = [300.0, 250.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values))


class TestTC07003:
    def test_returns_none(self):
        assert _ols_slope([300.0]) is None

    def test_warning_logged(self, caplog):
        with caplog.at_level(logging.WARNING, logger="src.descent_slope"):
            result = _ols_slope([300.0])
        assert result is None
        assert any("single-point" in msg.lower() or "l=1" in msg.lower()
                   for msg in caplog.messages)


class TestTC07004:
    """Empty window list (no anchors) → empty slopes list."""

    def test_empty_window_list_produces_empty_slopes(self):
        windows = {("V001", "P01"): []}
        slopes = compute_slopes(windows)
        assert slopes[("V001", "P01")] == []

    def test_empty_key_present_in_output(self):
        windows = {("V001", "P01"): []}
        slopes = compute_slopes(windows)
        assert ("V001", "P01") in slopes


class TestTC07005:
    def test_non_linear_matches_polyfit(self):
        values = [400.0, 360.0, 290.0, 195.0, 80.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values), rel=1e-9)

    def test_longer_window_matches_polyfit(self):
        values = [500.0, 480.0, 430.0, 350.0, 240.0, 110.0, 50.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values), rel=1e-9)


class TestTC07006:
    def test_nan_raises_slope_error(self):
        with pytest.raises(SlopeError):
            _ols_slope([300.0, float("nan"), 100.0])

    def test_all_nan_raises_slope_error(self):
        with pytest.raises(SlopeError):
            _ols_slope([float("nan"), float("nan")])

    def test_nan_in_compute_slopes_propagates(self):
        windows = {
            ("V001", "P01"): [_make_window([300.0, float("nan"), 100.0])]
        }
        with pytest.raises(SlopeError):
            compute_slopes(windows)


class TestTC07007:
    """Multiple (visit, point) pairs — mix of empty and single-window lists."""

    def test_mixed_output_keys(self):
        windows = {
            ("V001", "P01"): [_make_window([300.0, 200.0, 100.0])],
            ("V001", "P02"): [],
            ("V002", "P01"): [_make_window([400.0, 350.0])],
        }
        slopes = compute_slopes(windows)
        assert set(slopes.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}
        assert slopes[("V001", "P01")] == [pytest.approx(-100.0)]
        assert slopes[("V001", "P02")] == []
        assert slopes[("V002", "P01")] == [pytest.approx(-50.0)]


class TestTC07008:
    """All descent window lists empty → all slopes lists empty."""

    def test_all_empty_slopes(self):
        windows = {
            ("V001", "P01"): [],
            ("V001", "P02"): [],
        }
        slopes = compute_slopes(windows)
        assert all(s == [] for s in slopes.values())


class TestTC07009:
    def test_flat_window_slope_zero(self):
        assert _ols_slope([250.0, 250.0, 250.0, 250.0]) == pytest.approx(0.0, abs=1e-12)


class TestTC07010:
    """Multi-anchor series → list of slopes, one per anchor."""

    def test_two_anchors_two_slopes(self):
        windows = {
            ("V001", "P01"): [
                _make_window([300.0, 200.0, 100.0]),   # slope=-100
                _make_window([400.0, 350.0]),           # slope=-50
            ]
        }
        slopes = compute_slopes(windows)
        sl = slopes[("V001", "P01")]
        assert len(sl) == 2
        assert sl[0] == pytest.approx(-100.0)
        assert sl[1] == pytest.approx(-50.0)

    def test_single_point_anchor_gives_none_in_list(self):
        windows = {
            ("V001", "P01"): [
                _make_window([300.0]),       # single-point → None
                _make_window([400.0, 350.0]),
            ]
        }
        slopes = compute_slopes(windows)
        sl = slopes[("V001", "P01")]
        assert sl[0] is None
        assert sl[1] == pytest.approx(-50.0)
