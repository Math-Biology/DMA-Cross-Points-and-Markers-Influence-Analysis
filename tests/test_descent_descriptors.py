# LINKED-TO: [REQ-CPM-IA-P26.0008]
"""
Unit tests for src/descent_descriptors.py — Module 08: Descent Shape Descriptors.

All test IDs trace to .agent/modules/08_descent_descriptors.md.
"""

import pytest

from src.descent_window import DescentWindow
from src.trigger_detection import TriggerResult
from src.descent_descriptors import DescriptorError, DescentDescriptor, compute_descriptors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_window(values: list, truncated: bool = False) -> DescentWindow:
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
    )


def _make_trigger(anchor_value, anchor_index=0, anchor_marker="M1", no_effect=False):
    return TriggerResult(
        first_positive_marker=None if no_effect else anchor_marker,
        first_positive_index=None if no_effect else anchor_index,
        first_positive_value=None if no_effect else anchor_value,
        no_cross_marker_effect=no_effect,
    )


# ---------------------------------------------------------------------------
# TC-08-001 — Standard descent window
# ---------------------------------------------------------------------------

class TestTC08001:
    """TC-08-001: anchor=300, window=[300,250,200,150] -> depth=150, length=4, mpsd=50.0."""

    def test_depth(self):
        windows = {("V001", "P01"): _make_window([300.0, 250.0, 200.0, 150.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_depth == pytest.approx(150.0)

    def test_length(self):
        windows = {("V001", "P01"): _make_window([300.0, 250.0, 200.0, 150.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_length == 4

    def test_mean_per_step_decrease(self):
        windows = {("V001", "P01"): _make_window([300.0, 250.0, 200.0, 150.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.mean_per_step_decrease == pytest.approx(50.0)

    def test_returns_frozen_dataclass(self):
        windows = {("V001", "P01"): _make_window([300.0, 250.0, 200.0, 150.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert isinstance(d, DescentDescriptor)


# ---------------------------------------------------------------------------
# TC-08-002 — Single-point window (anchor only)
# ---------------------------------------------------------------------------

class TestTC08002:
    """TC-08-002: Window of length 1 -> depth=0, length=1, mpsd=0.0."""

    def test_depth_zero(self):
        windows = {("V001", "P01"): _make_window([300.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_depth == pytest.approx(0.0)

    def test_length_one(self):
        windows = {("V001", "P01"): _make_window([300.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_length == 1

    def test_mpsd_zero(self):
        windows = {("V001", "P01"): _make_window([300.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.mean_per_step_decrease == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# TC-08-003 — None descent window
# ---------------------------------------------------------------------------

class TestTC08003:
    """TC-08-003: descent_windows value is None -> descriptors[(v,p)] = None."""

    def test_none_window_produces_none_descriptor(self):
        windows = {("V001", "P01"): None}
        triggers = {("V001", "P01"): _make_trigger(None, no_effect=True)}
        result = compute_descriptors(windows, triggers)
        assert result[("V001", "P01")] is None

    def test_none_key_present_in_output(self):
        windows = {("V001", "P01"): None}
        triggers = {("V001", "P01"): _make_trigger(None, no_effect=True)}
        result = compute_descriptors(windows, triggers)
        assert ("V001", "P01") in result


# ---------------------------------------------------------------------------
# TC-08-004 — NaN in window
# ---------------------------------------------------------------------------

class TestTC08004:
    """TC-08-004: NaN in window_values -> DescriptorError raised."""

    def test_nan_raises_descriptor_error(self):
        windows = {("V001", "P01"): _make_window([300.0, float("nan"), 150.0])}
        triggers = {("V001", "P01"): _make_trigger(300.0)}
        with pytest.raises(DescriptorError):
            compute_descriptors(windows, triggers)

    def test_all_nan_raises_descriptor_error(self):
        windows = {("V001", "P01"): _make_window([float("nan"), float("nan")])}
        triggers = {("V001", "P01"): _make_trigger(float("nan"))}
        with pytest.raises(DescriptorError):
            compute_descriptors(windows, triggers)


# ---------------------------------------------------------------------------
# TC-08-005 — Missing anchor value
# ---------------------------------------------------------------------------

class TestTC08005:
    """TC-08-005: first_positive_value is None with non-None window -> DescriptorError."""

    def test_missing_anchor_raises_descriptor_error(self):
        windows = {("V001", "P01"): _make_window([300.0, 200.0])}
        # Simulate corrupt upstream: non-None window but no anchor
        corrupt_trigger = TriggerResult(
            first_positive_marker="M1",
            first_positive_index=0,
            first_positive_value=None,   # missing
            no_cross_marker_effect=False,
        )
        triggers = {("V001", "P01"): corrupt_trigger}
        with pytest.raises(DescriptorError):
            compute_descriptors(windows, triggers)


# ---------------------------------------------------------------------------
# TC-08-006 — Non-monotone window (minimum not at last position)
# ---------------------------------------------------------------------------

class TestTC08006:
    """TC-08-006: min(window_values) not at last index -> depth uses global min."""

    def test_depth_uses_global_min(self):
        # Epsilon-bounded rise mid-window: [400, 390, 395, 380]
        # min = 380 (last), depth = 400 - 380 = 20
        # But test a case where min is in the middle: [400, 350, 360, 370]
        # min = 350 (index 1), depth = 400 - 350 = 50
        windows = {("V001", "P01"): _make_window([400.0, 350.0, 360.0, 370.0])}
        triggers = {("V001", "P01"): _make_trigger(400.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_depth == pytest.approx(50.0)
        assert d.descent_length == 4
        assert d.mean_per_step_decrease == pytest.approx(50.0 / 3)

    def test_depth_not_anchor_minus_last(self):
        # Confirm depth != anchor - last when min is not last
        windows = {("V001", "P01"): _make_window([400.0, 350.0, 360.0, 370.0])}
        triggers = {("V001", "P01"): _make_trigger(400.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        # anchor - last = 400 - 370 = 30 ≠ 50 (the real depth)
        assert d.descent_depth != pytest.approx(400.0 - 370.0)


# ---------------------------------------------------------------------------
# TC-08-007 — Two-point window
# ---------------------------------------------------------------------------

class TestTC08007:
    """TC-08-007: Two-point window [400, 300] -> depth=100, length=2, mpsd=100.0."""

    def test_two_point_descriptors(self):
        windows = {("V001", "P01"): _make_window([400.0, 300.0])}
        triggers = {("V001", "P01"): _make_trigger(400.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")]
        assert d.descent_depth == pytest.approx(100.0)
        assert d.descent_length == 2
        assert d.mean_per_step_decrease == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# TC-08-008 — Mixed valid and None windows
# ---------------------------------------------------------------------------

class TestTC08008:
    """TC-08-008: Multiple (visit, point) pairs — mix of None and valid."""

    def setup_method(self):
        self.windows = {
            ("V001", "P01"): _make_window([300.0, 250.0, 200.0, 150.0]),
            ("V001", "P02"): None,
            ("V002", "P01"): _make_window([500.0, 400.0]),
        }
        self.triggers = {
            ("V001", "P01"): _make_trigger(300.0),
            ("V001", "P02"): _make_trigger(None, no_effect=True),
            ("V002", "P01"): _make_trigger(500.0),
        }

    def test_output_keys(self):
        result = compute_descriptors(self.windows, self.triggers)
        assert set(result.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}

    def test_none_entry(self):
        result = compute_descriptors(self.windows, self.triggers)
        assert result[("V001", "P02")] is None

    def test_valid_entry_v001_p01(self):
        result = compute_descriptors(self.windows, self.triggers)
        d = result[("V001", "P01")]
        assert d.descent_depth == pytest.approx(150.0)
        assert d.descent_length == 4
        assert d.mean_per_step_decrease == pytest.approx(50.0)

    def test_valid_entry_v002_p01(self):
        result = compute_descriptors(self.windows, self.triggers)
        d = result[("V002", "P01")]
        assert d.descent_depth == pytest.approx(100.0)
        assert d.descent_length == 2
        assert d.mean_per_step_decrease == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# TC-08-009 — All None windows
# ---------------------------------------------------------------------------

class TestTC08009:
    """TC-08-009: All descent windows are None -> all descriptors are None."""

    def test_all_none_descriptors(self):
        windows = {
            ("V001", "P01"): None,
            ("V001", "P02"): None,
            ("V002", "P01"): None,
        }
        triggers = {
            ("V001", "P01"): _make_trigger(None, no_effect=True),
            ("V001", "P02"): _make_trigger(None, no_effect=True),
            ("V002", "P01"): _make_trigger(None, no_effect=True),
        }
        result = compute_descriptors(windows, triggers)
        assert all(d is None for d in result.values())
        assert len(result) == 3
