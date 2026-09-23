# LINKED-TO: [REQ-CPM-IA-P26.0009]
"""Unit tests for src/variance_indicator.py — Module 09."""

import math
import statistics

import pytest

from src.descent_window import DescentWindow
from src.trigger_detection import Anchor, TriggerResult
from src.variance_indicator import VarianceIndicator, compute_variance_indicators


def _make_window(values, truncated=False, close_reason="end"):
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
        window_close_reason=close_reason,
    )


def _make_trigger_single(anchor_index, anchor_value, marker="M1", no_effect=False):
    if no_effect:
        return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)
    anchor = Anchor(marker=marker, index=anchor_index, value=anchor_value)
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


class TestTC09001:
    """TC-09-001: before=[100,120], after=[300,250,200] -> correct sample variances."""

    def setup_method(self):
        self.sequences = {("V001", "P01"): [100.0, 120.0, 300.0, 250.0, 200.0]}
        self.triggers  = {("V001", "P01"): _make_trigger_single(2, 300.0)}
        self.windows   = {("V001", "P01"): [_make_window([300.0, 250.0, 200.0])]}

    def test_variance_before(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")][0]
        assert ind.variance_before == pytest.approx(200.0)

    def test_variance_after(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")][0]
        assert ind.variance_after == pytest.approx(2500.0)

    def test_matches_statistics_module(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")][0]
        assert ind.variance_before == pytest.approx(statistics.variance([100.0, 120.0]))
        assert ind.variance_after  == pytest.approx(statistics.variance([300.0, 250.0, 200.0]))

    def test_returns_frozen_dataclass(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert isinstance(result[("V001", "P01")][0], VarianceIndicator)


class TestTC09002:
    """TC-09-002: Anchor at index 0 -> variance_before=None."""

    def test_variance_before_none(self):
        sequences = {("V001", "P01"): [300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(0, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0, 250.0, 200.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_before is None

    def test_variance_after_computed(self):
        sequences = {("V001", "P01"): [300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(0, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0, 250.0, 200.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_after == pytest.approx(statistics.variance([300.0, 250.0, 200.0]))


class TestTC09003:
    """TC-09-003: Window of length 1 -> variance_after=None."""

    def test_variance_after_none(self):
        sequences = {("V001", "P01"): [100.0, 120.0, 300.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(2, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_after is None


class TestTC09004:
    """TC-09-004: no_cross_marker_effect=True -> empty list."""

    def test_empty_list_for_no_effect(self):
        sequences = {("V001", "P01"): [100.0, 150.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(None, None, no_effect=True)}
        windows   = {("V001", "P01"): []}
        result = compute_variance_indicators(sequences, triggers, windows)
        assert result[("V001", "P01")] == []

    def test_key_present_in_output(self):
        sequences = {("V001", "P01"): [100.0, 150.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(None, None, no_effect=True)}
        windows   = {("V001", "P01"): []}
        result = compute_variance_indicators(sequences, triggers, windows)
        assert ("V001", "P01") in result


class TestTC09005:
    """TC-09-005: Before segment has 1 non-NaN value -> variance_before=None."""

    def test_single_before_value_returns_none(self):
        sequences = {("V001", "P01"): [120.0, 300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(1, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0, 250.0, 200.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_before is None


class TestTC09006:
    """TC-09-006: NaN in before segment stripped; variance computed on clean values."""

    def test_nan_stripped_before_segment(self):
        sequences = {("V001", "P01"): [float("nan"), 100.0, 150.0, 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(3, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0, 250.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_before == pytest.approx(statistics.variance([100.0, 150.0]))


class TestTC09007:
    """TC-09-007: Before segment all NaN -> variance_before=None."""

    def test_all_nan_before_returns_none(self):
        sequences = {("V001", "P01"): [float("nan"), float("nan"), 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger_single(2, 300.0)}
        windows   = {("V001", "P01"): [_make_window([300.0, 250.0])]}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]
        assert ind.variance_before is None
        assert ind.variance_after == pytest.approx(statistics.variance([300.0, 250.0]))


class TestTC09008:
    """TC-09-008: Multiple (visit, point) pairs — mix of empty and valid."""

    def setup_method(self):
        self.sequences = {
            ("V001", "P01"): [100.0, 120.0, 300.0, 250.0, 200.0],
            ("V001", "P02"): [80.0, 90.0, 85.0],
            ("V002", "P01"): [200.0, 400.0, 350.0],
        }
        self.triggers = {
            ("V001", "P01"): _make_trigger_single(2, 300.0),
            ("V001", "P02"): _make_trigger_single(None, None, no_effect=True),
            ("V002", "P01"): _make_trigger_single(1, 400.0),
        }
        self.windows = {
            ("V001", "P01"): [_make_window([300.0, 250.0, 200.0])],
            ("V001", "P02"): [],
            ("V002", "P01"): [_make_window([400.0, 350.0])],
        }

    def test_output_keys(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert set(result.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}

    def test_empty_list_for_no_effect(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert result[("V001", "P02")] == []

    def test_valid_v001_p01(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")][0]
        assert ind.variance_before == pytest.approx(200.0)
        assert ind.variance_after  == pytest.approx(2500.0)

    def test_valid_v002_p01(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V002", "P01")][0]
        assert ind.variance_before is None
        assert ind.variance_after == pytest.approx(statistics.variance([400.0, 350.0]))


class TestTC09009:
    """TC-09-009: All entries no_cross_marker_effect=True -> all empty lists."""

    def test_all_empty(self):
        sequences = {
            ("V001", "P01"): [100.0, 200.0],
            ("V001", "P02"): [110.0, 210.0],
        }
        triggers = {
            ("V001", "P01"): _make_trigger_single(None, None, no_effect=True),
            ("V001", "P02"): _make_trigger_single(None, None, no_effect=True),
        }
        windows = {
            ("V001", "P01"): [],
            ("V001", "P02"): [],
        }
        result = compute_variance_indicators(sequences, triggers, windows)
        assert all(v == [] for v in result.values())


class TestTC09010:
    """TC-09-010: variance_ratio computed correctly."""

    def _compute(self, before_vals, after_vals, anchor_idx, anchor_val=301.0):
        seq = before_vals + [anchor_val] + after_vals
        anchor = Anchor(marker="M_anchor", index=anchor_idx, value=anchor_val)
        trigger = TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)
        sequences = {("V001", "P01"): seq}
        triggers = {("V001", "P01"): trigger}
        window = DescentWindow(
            window_values=[anchor_val] + after_vals,
            window_length=1 + len(after_vals),
            truncated_by_n_max=False,
            window_close_reason="end",
        )
        windows = {("V001", "P01"): [window]}
        return compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")][0]

    def test_ratio_computed_when_both_valid(self):
        import statistics as _s
        ind = self._compute([100.0, 120.0], [250.0, 200.0], anchor_idx=2)
        vb = _s.variance([100.0, 120.0])
        va = _s.variance([301.0, 250.0, 200.0])
        assert ind.variance_ratio == pytest.approx(va / vb)

    def test_ratio_none_when_before_is_none(self):
        ind = self._compute([], [250.0, 200.0], anchor_idx=0)
        assert ind.variance_ratio is None

    def test_ratio_none_when_after_is_none(self):
        ind = self._compute([100.0, 120.0], [], anchor_idx=2)
        assert ind.variance_ratio is None

    def test_ratio_none_when_variance_before_zero(self):
        ind = self._compute([200.0, 200.0], [250.0, 200.0], anchor_idx=2)
        assert ind.variance_ratio is None


class TestTC09011:
    """TC-09-011: Multi-anchor series -> list with one VarianceIndicator per anchor."""

    def test_two_anchors_two_indicators(self):
        # sequence: [100, 120, 300(anchor0), 250, 200, 400(anchor1), 350]
        seq = [100.0, 120.0, 300.0, 250.0, 200.0, 400.0, 350.0]
        a0 = Anchor(marker="M1", index=2, value=300.0)
        a1 = Anchor(marker="M2", index=5, value=400.0)
        trigger = TriggerResult(anchors=[a0, a1], positives_count=2, no_cross_marker_effect=False)
        sequences = {("V001", "P01"): seq}
        triggers  = {("V001", "P01"): trigger}
        windows   = {
            ("V001", "P01"): [
                _make_window([300.0, 250.0, 200.0]),
                _make_window([400.0, 350.0]),
            ]
        }
        result = compute_variance_indicators(sequences, triggers, windows)
        vi_list = result[("V001", "P01")]
        assert len(vi_list) == 2
        # anchor0: before=[100,120], after=[300,250,200]
        assert vi_list[0].variance_before == pytest.approx(statistics.variance([100.0, 120.0]))
        assert vi_list[0].variance_after  == pytest.approx(statistics.variance([300.0, 250.0, 200.0]))
        # anchor1: before=[100,120,300,250,200], after=[400,350]
        assert vi_list[1].variance_before == pytest.approx(statistics.variance([100.0, 120.0, 300.0, 250.0, 200.0]))
        assert vi_list[1].variance_after  == pytest.approx(statistics.variance([400.0, 350.0]))
