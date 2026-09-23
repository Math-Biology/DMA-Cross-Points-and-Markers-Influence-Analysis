# LINKED-TO: [REQ-CPM-IA-P26.0008]
"""Unit tests for src/descent_descriptors.py — Module 08: Descent Shape Descriptors."""

import pytest

from src.descent_window import DescentWindow
from src.trigger_detection import Anchor, TriggerResult
from src.descent_descriptors import DescriptorError, DescentDescriptor, compute_descriptors


def _make_window(values, truncated=False, close_reason="end"):
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
        window_close_reason=close_reason,
    )


def _make_trigger_single(anchor_value, anchor_index=0, anchor_marker="M1", no_effect=False):
    if no_effect:
        return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)
    anchor = Anchor(marker=anchor_marker, index=anchor_index, value=anchor_value)
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


class TestTC08001:
    """TC-08-001: anchor=300, window=[300,250,200,150] -> depth=150, length=4, mpsd=50.0."""

    def setup_method(self):
        self.windows = {("V001", "P01"): [_make_window([300.0, 250.0, 200.0, 150.0])]}
        self.triggers = {("V001", "P01"): _make_trigger_single(300.0)}

    def test_depth(self):
        d = compute_descriptors(self.windows, self.triggers)[("V001", "P01")][0]
        assert d.descent_depth == pytest.approx(150.0)

    def test_length(self):
        d = compute_descriptors(self.windows, self.triggers)[("V001", "P01")][0]
        assert d.descent_length == 4

    def test_mean_per_step_decrease(self):
        d = compute_descriptors(self.windows, self.triggers)[("V001", "P01")][0]
        assert d.mean_per_step_decrease == pytest.approx(50.0)

    def test_returns_frozen_dataclass(self):
        d = compute_descriptors(self.windows, self.triggers)[("V001", "P01")][0]
        assert isinstance(d, DescentDescriptor)


class TestTC08002:
    """TC-08-002: Single-point window -> depth=0, length=1, mpsd=0.0."""

    def test_depth_zero(self):
        windows = {("V001", "P01"): [_make_window([300.0])]}
        triggers = {("V001", "P01"): _make_trigger_single(300.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")][0]
        assert d.descent_depth == pytest.approx(0.0)
        assert d.descent_length == 1
        assert d.mean_per_step_decrease == pytest.approx(0.0)


class TestTC08003:
    """TC-08-003: Empty window list (no_cross_marker_effect) -> empty list."""

    def test_empty_list_for_no_effect(self):
        windows = {("V001", "P01"): []}
        triggers = {("V001", "P01"): _make_trigger_single(None, no_effect=True)}
        result = compute_descriptors(windows, triggers)
        assert result[("V001", "P01")] == []

    def test_key_present_in_output(self):
        windows = {("V001", "P01"): []}
        triggers = {("V001", "P01"): _make_trigger_single(None, no_effect=True)}
        result = compute_descriptors(windows, triggers)
        assert ("V001", "P01") in result


class TestTC08004:
    """TC-08-004: NaN in window_values -> DescriptorError raised."""

    def test_nan_raises_descriptor_error(self):
        windows = {("V001", "P01"): [_make_window([300.0, float("nan"), 150.0])]}
        triggers = {("V001", "P01"): _make_trigger_single(300.0)}
        with pytest.raises(DescriptorError):
            compute_descriptors(windows, triggers)


class TestTC08006:
    """TC-08-006: min(window_values) not at last index -> depth uses global min."""

    def test_depth_uses_global_min(self):
        windows = {("V001", "P01"): [_make_window([400.0, 350.0, 360.0, 370.0])]}
        triggers = {("V001", "P01"): _make_trigger_single(400.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")][0]
        assert d.descent_depth == pytest.approx(50.0)
        assert d.descent_length == 4
        assert d.mean_per_step_decrease == pytest.approx(50.0 / 3)


class TestTC08007:
    """TC-08-007: Two-point window [400, 300] -> depth=100, length=2, mpsd=100.0."""

    def test_two_point_descriptors(self):
        windows = {("V001", "P01"): [_make_window([400.0, 300.0])]}
        triggers = {("V001", "P01"): _make_trigger_single(400.0)}
        d = compute_descriptors(windows, triggers)[("V001", "P01")][0]
        assert d.descent_depth == pytest.approx(100.0)
        assert d.descent_length == 2
        assert d.mean_per_step_decrease == pytest.approx(100.0)


class TestTC08008:
    """TC-08-008: Multiple (visit, point) pairs — mix of empty and valid."""

    def setup_method(self):
        self.windows = {
            ("V001", "P01"): [_make_window([300.0, 250.0, 200.0, 150.0])],
            ("V001", "P02"): [],
            ("V002", "P01"): [_make_window([500.0, 400.0])],
        }
        self.triggers = {
            ("V001", "P01"): _make_trigger_single(300.0),
            ("V001", "P02"): _make_trigger_single(None, no_effect=True),
            ("V002", "P01"): _make_trigger_single(500.0),
        }

    def test_output_keys(self):
        result = compute_descriptors(self.windows, self.triggers)
        assert set(result.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}

    def test_empty_list_entry(self):
        result = compute_descriptors(self.windows, self.triggers)
        assert result[("V001", "P02")] == []

    def test_valid_entry_v001_p01(self):
        result = compute_descriptors(self.windows, self.triggers)
        d = result[("V001", "P01")][0]
        assert d.descent_depth == pytest.approx(150.0)
        assert d.descent_length == 4
        assert d.mean_per_step_decrease == pytest.approx(50.0)

    def test_valid_entry_v002_p01(self):
        result = compute_descriptors(self.windows, self.triggers)
        d = result[("V002", "P01")][0]
        assert d.descent_depth == pytest.approx(100.0)
        assert d.descent_length == 2
        assert d.mean_per_step_decrease == pytest.approx(100.0)


class TestTC08009:
    """TC-08-009: Multi-anchor series -> list with one descriptor per anchor."""

    def test_two_anchors_two_descriptors(self):
        from src.trigger_detection import Anchor, TriggerResult
        anchor0 = Anchor(marker="M1", index=0, value=400.0)
        anchor1 = Anchor(marker="M3", index=2, value=500.0)
        trigger = TriggerResult(
            anchors=[anchor0, anchor1],
            positives_count=2,
            no_cross_marker_effect=False,
        )
        windows = {
            ("V001", "P01"): [
                _make_window([400.0, 350.0, 300.0]),  # anchor 0
                _make_window([500.0, 400.0]),          # anchor 1
            ]
        }
        triggers = {("V001", "P01"): trigger}
        result = compute_descriptors(windows, triggers)
        desc_list = result[("V001", "P01")]
        assert len(desc_list) == 2
        assert desc_list[0].descent_depth == pytest.approx(100.0)
        assert desc_list[1].descent_depth == pytest.approx(100.0)
