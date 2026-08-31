# LINKED-TO: [REQ-CPM-IA-P26.0007]
"""
Unit tests for src/descent_slope.py — Module 07: Descent Slope Computation.

Cross-validates the closed-form OLS implementation against numpy.polyfit
as an independent reference. All test IDs trace to .agent/modules/07_descent_slope.md.
"""

import logging
import math

import numpy as np
import pytest

from src.descent_window import DescentWindow
from src.descent_slope import SlopeError, _ols_slope, compute_slopes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_window(values: list, truncated: bool = False) -> DescentWindow:
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
    )


def _polyfit_slope(values: list) -> float:
    """Independent OLS reference via numpy.polyfit."""
    n = len(values)
    x = list(range(n))
    return float(np.polyfit(x, values, 1)[0])


# ---------------------------------------------------------------------------
# TC-07-001 — Perfect linear descent
# ---------------------------------------------------------------------------

class TestTC07001:
    """TC-07-001: Window=[300, 200, 100] (perfect linear descent) -> slope=-100.0."""

    def test_slope_value(self):
        slope = _ols_slope([300.0, 200.0, 100.0])
        assert slope == pytest.approx(-100.0)

    def test_matches_polyfit(self):
        values = [300.0, 200.0, 100.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values))


# ---------------------------------------------------------------------------
# TC-07-002 — Two-point window (secant)
# ---------------------------------------------------------------------------

class TestTC07002:
    """TC-07-002: Window=[300, 250] (two points) -> slope=-50.0 (secant)."""

    def test_slope_value(self):
        slope = _ols_slope([300.0, 250.0])
        assert slope == pytest.approx(-50.0)

    def test_matches_polyfit(self):
        values = [300.0, 250.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values))


# ---------------------------------------------------------------------------
# TC-07-003 — Single-point window
# ---------------------------------------------------------------------------

class TestTC07003:
    """TC-07-003: Window of length 1 -> slope=None and WARNING logged."""

    def test_returns_none(self):
        assert _ols_slope([300.0]) is None

    def test_warning_logged(self, caplog):
        with caplog.at_level(logging.WARNING, logger="src.descent_slope"):
            result = _ols_slope([300.0])
        assert result is None
        assert any("single-point" in msg.lower() or "l=1" in msg.lower()
                   for msg in caplog.messages)


# ---------------------------------------------------------------------------
# TC-07-004 — None descent window
# ---------------------------------------------------------------------------

class TestTC07004:
    """TC-07-004: descent_windows value is None -> slopes[(v,p)] = None."""

    def test_none_window_produces_none_slope(self):
        windows = {("V001", "P01"): None}
        slopes = compute_slopes(windows)
        assert slopes[("V001", "P01")] is None

    def test_none_key_present_in_output(self):
        windows = {("V001", "P01"): None}
        slopes = compute_slopes(windows)
        assert ("V001", "P01") in slopes


# ---------------------------------------------------------------------------
# TC-07-005 — Non-linear window (OLS cross-check against numpy.polyfit)
# ---------------------------------------------------------------------------

class TestTC07005:
    """TC-07-005: Non-linear window — slope must match numpy.polyfit reference."""

    def test_non_linear_matches_polyfit(self):
        values = [400.0, 360.0, 290.0, 195.0, 80.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values), rel=1e-9)

    def test_longer_window_matches_polyfit(self):
        values = [500.0, 480.0, 430.0, 350.0, 240.0, 110.0, 50.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values), rel=1e-9)


# ---------------------------------------------------------------------------
# TC-07-006 — NaN in window raises SlopeError
# ---------------------------------------------------------------------------

class TestTC07006:
    """TC-07-006: NaN value in window -> SlopeError raised."""

    def test_nan_raises_slope_error(self):
        with pytest.raises(SlopeError):
            _ols_slope([300.0, float("nan"), 100.0])

    def test_all_nan_raises_slope_error(self):
        with pytest.raises(SlopeError):
            _ols_slope([float("nan"), float("nan")])

    def test_nan_in_compute_slopes_propagates(self):
        windows = {
            ("V001", "P01"): _make_window([300.0, float("nan"), 100.0])
        }
        with pytest.raises(SlopeError):
            compute_slopes(windows)


# ---------------------------------------------------------------------------
# TC-07-007 — Mixed valid and None windows
# ---------------------------------------------------------------------------

class TestTC07007:
    """TC-07-007: Multiple (visit, point) pairs — mix of None and valid windows."""

    def test_mixed_output_keys(self):
        windows = {
            ("V001", "P01"): _make_window([300.0, 200.0, 100.0]),
            ("V001", "P02"): None,
            ("V002", "P01"): _make_window([400.0, 350.0]),
        }
        slopes = compute_slopes(windows)
        assert set(slopes.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}
        assert slopes[("V001", "P01")] == pytest.approx(-100.0)
        assert slopes[("V001", "P02")] is None
        assert slopes[("V002", "P01")] == pytest.approx(-50.0)


# ---------------------------------------------------------------------------
# TC-07-008 — All None windows
# ---------------------------------------------------------------------------

class TestTC07008:
    """TC-07-008: All descent windows are None -> all slopes are None."""

    def test_all_none_slopes(self):
        windows = {
            ("V001", "P01"): None,
            ("V001", "P02"): None,
            ("V002", "P01"): None,
        }
        slopes = compute_slopes(windows)
        assert all(s is None for s in slopes.values())
        assert len(slopes) == 3


# ---------------------------------------------------------------------------
# TC-07-009 — Flat window (slope = 0)
# ---------------------------------------------------------------------------

class TestTC07009:
    """TC-07-009: All values equal -> slope = 0.0."""

    def test_flat_window_slope_zero(self):
        slope = _ols_slope([250.0, 250.0, 250.0, 250.0])
        assert slope == pytest.approx(0.0, abs=1e-12)

    def test_flat_window_matches_polyfit(self):
        values = [250.0, 250.0, 250.0, 250.0]
        assert _ols_slope(values) == pytest.approx(_polyfit_slope(values), abs=1e-12)
