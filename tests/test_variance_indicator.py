# LINKED-TO: [REQ-CPM-IA-P26.0009]
"""
Unit tests for src/variance_indicator.py — Module 09: Pre/Post Positive Variance Indicator.

All test IDs trace to .agent/modules/09_variance_indicator.md.
"""

import math
import statistics

import pytest

from src.descent_window import DescentWindow
from src.trigger_detection import TriggerResult
from src.variance_indicator import VarianceIndicator, compute_variance_indicators


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_window(values: list, truncated: bool = False) -> DescentWindow:
    return DescentWindow(
        window_values=values,
        window_length=len(values),
        truncated_by_n_max=truncated,
    )


def _make_trigger(anchor_index, anchor_value, marker="M1", no_effect=False):
    return TriggerResult(
        first_positive_marker=None if no_effect else marker,
        first_positive_index=None if no_effect else anchor_index,
        first_positive_value=None if no_effect else anchor_value,
        no_cross_marker_effect=no_effect,
    )


# ---------------------------------------------------------------------------
# TC-09-001 — Standard case: valid before and after segments
# ---------------------------------------------------------------------------

class TestTC09001:
    """TC-09-001: before=[100,120], after=[300,250,200] -> correct sample variances."""

    # before=[100,120]: mean=110, var=((100-110)^2+(120-110)^2)/(2-1) = 200.0
    # after=[300,250,200]: mean=250, var=((50)^2+(0)^2+(-50)^2)/(3-1) = 2500.0

    def setup_method(self):
        # Full sequence: [100, 120, 300(anchor), 250, 200]
        # anchor_index=2, window=[300,250,200]
        self.sequences = {("V001", "P01"): [100.0, 120.0, 300.0, 250.0, 200.0]}
        self.triggers  = {("V001", "P01"): _make_trigger(2, 300.0)}
        self.windows   = {("V001", "P01"): _make_window([300.0, 250.0, 200.0])}

    def test_variance_before(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")]
        assert ind.variance_before == pytest.approx(200.0)

    def test_variance_after(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")]
        assert ind.variance_after == pytest.approx(2500.0)

    def test_matches_statistics_module(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")]
        assert ind.variance_before == pytest.approx(statistics.variance([100.0, 120.0]))
        assert ind.variance_after  == pytest.approx(statistics.variance([300.0, 250.0, 200.0]))

    def test_returns_frozen_dataclass(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert isinstance(result[("V001", "P01")], VarianceIndicator)


# ---------------------------------------------------------------------------
# TC-09-002 — Anchor at index 0 (no before segment)
# ---------------------------------------------------------------------------

class TestTC09002:
    """TC-09-002: Anchor at index 0 -> variance_before=None."""

    def test_variance_before_none(self):
        sequences = {("V001", "P01"): [300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger(0, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0, 200.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before is None

    def test_variance_after_computed(self):
        sequences = {("V001", "P01"): [300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger(0, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0, 200.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_after == pytest.approx(statistics.variance([300.0, 250.0, 200.0]))


# ---------------------------------------------------------------------------
# TC-09-003 — Descent window length 1
# ---------------------------------------------------------------------------

class TestTC09003:
    """TC-09-003: Window of length 1 -> variance_after=None."""

    def test_variance_after_none(self):
        sequences = {("V001", "P01"): [100.0, 120.0, 300.0]}
        triggers  = {("V001", "P01"): _make_trigger(2, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_after is None

    def test_variance_before_computed(self):
        sequences = {("V001", "P01"): [100.0, 120.0, 300.0]}
        triggers  = {("V001", "P01"): _make_trigger(2, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before == pytest.approx(statistics.variance([100.0, 120.0]))


# ---------------------------------------------------------------------------
# TC-09-004 — no_cross_marker_effect=True
# ---------------------------------------------------------------------------

class TestTC09004:
    """TC-09-004: no_cross_marker_effect=True -> variance_indicators[(v,p)] = None."""

    def test_none_entry(self):
        sequences = {("V001", "P01"): [100.0, 150.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger(None, None, no_effect=True)}
        windows   = {("V001", "P01"): None}
        result = compute_variance_indicators(sequences, triggers, windows)
        assert result[("V001", "P01")] is None

    def test_key_present_in_output(self):
        sequences = {("V001", "P01"): [100.0, 150.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger(None, None, no_effect=True)}
        windows   = {("V001", "P01"): None}
        result = compute_variance_indicators(sequences, triggers, windows)
        assert ("V001", "P01") in result


# ---------------------------------------------------------------------------
# TC-09-005 — Before segment has exactly 1 non-NaN value
# ---------------------------------------------------------------------------

class TestTC09005:
    """TC-09-005: Before segment has 1 non-NaN value -> variance_before=None."""

    def test_single_before_value_returns_none(self):
        # sequence: [120, 300(anchor), 250, 200] — before=[120], 1 value only
        sequences = {("V001", "P01"): [120.0, 300.0, 250.0, 200.0]}
        triggers  = {("V001", "P01"): _make_trigger(1, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0, 200.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before is None


# ---------------------------------------------------------------------------
# TC-09-006 — NaN in before segment (stripped, enough remain)
# ---------------------------------------------------------------------------

class TestTC09006:
    """TC-09-006: NaN in before segment stripped; variance computed on clean values."""

    def test_nan_stripped_before_segment(self):
        # before_raw = [nan, 100.0, 150.0], after strip = [100.0, 150.0]
        # variance([100,150]) = ((100-125)^2 + (150-125)^2)/1 = (625+625) = 1250.0
        sequences = {("V001", "P01"): [float("nan"), 100.0, 150.0, 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger(3, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before == pytest.approx(statistics.variance([100.0, 150.0]))

    def test_nan_stripped_value(self):
        sequences = {("V001", "P01"): [float("nan"), 100.0, 150.0, 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger(3, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before == pytest.approx(1250.0)


# ---------------------------------------------------------------------------
# TC-09-007 — Before segment entirely NaN
# ---------------------------------------------------------------------------

class TestTC09007:
    """TC-09-007: Before segment all NaN -> stripped to empty -> variance_before=None."""

    def test_all_nan_before_returns_none(self):
        sequences = {("V001", "P01"): [float("nan"), float("nan"), 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger(2, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_before is None

    def test_after_still_computed(self):
        sequences = {("V001", "P01"): [float("nan"), float("nan"), 300.0, 250.0]}
        triggers  = {("V001", "P01"): _make_trigger(2, 300.0)}
        windows   = {("V001", "P01"): _make_window([300.0, 250.0])}
        ind = compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]
        assert ind.variance_after == pytest.approx(statistics.variance([300.0, 250.0]))


# ---------------------------------------------------------------------------
# TC-09-008 — Mixed None/valid (visit, point) pairs
# ---------------------------------------------------------------------------

class TestTC09008:
    """TC-09-008: Multiple (visit, point) pairs — mix of None and valid."""

    def setup_method(self):
        self.sequences = {
            ("V001", "P01"): [100.0, 120.0, 300.0, 250.0, 200.0],
            ("V001", "P02"): [80.0, 90.0, 85.0],
            ("V002", "P01"): [200.0, 400.0, 350.0],
        }
        self.triggers = {
            ("V001", "P01"): _make_trigger(2, 300.0),
            ("V001", "P02"): _make_trigger(None, None, no_effect=True),
            ("V002", "P01"): _make_trigger(1, 400.0),
        }
        self.windows = {
            ("V001", "P01"): _make_window([300.0, 250.0, 200.0]),
            ("V001", "P02"): None,
            ("V002", "P01"): _make_window([400.0, 350.0]),
        }

    def test_output_keys(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert set(result.keys()) == {("V001", "P01"), ("V001", "P02"), ("V002", "P01")}

    def test_none_for_no_effect(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        assert result[("V001", "P02")] is None

    def test_valid_v001_p01(self):
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V001", "P01")]
        assert ind.variance_before == pytest.approx(200.0)
        assert ind.variance_after  == pytest.approx(2500.0)

    def test_valid_v002_p01(self):
        # before=[200], single value -> None; after=[400,350]
        result = compute_variance_indicators(self.sequences, self.triggers, self.windows)
        ind = result[("V002", "P01")]
        assert ind.variance_before is None
        assert ind.variance_after == pytest.approx(statistics.variance([400.0, 350.0]))


# ---------------------------------------------------------------------------
# TC-09-009 — All no_cross_marker_effect=True
# ---------------------------------------------------------------------------

class TestTC09009:
    """TC-09-009: All entries no_cross_marker_effect=True -> all indicators None."""

    def test_all_none(self):
        sequences = {
            ("V001", "P01"): [100.0, 200.0],
            ("V001", "P02"): [110.0, 210.0],
        }
        triggers = {
            ("V001", "P01"): _make_trigger(None, None, no_effect=True),
            ("V001", "P02"): _make_trigger(None, None, no_effect=True),
        }
        windows = {
            ("V001", "P01"): None,
            ("V001", "P02"): None,
        }
        result = compute_variance_indicators(sequences, triggers, windows)
        assert all(v is None for v in result.values())
        assert len(result) == 2


# ---------------------------------------------------------------------------
# TC-09-010 — variance_ratio field
# ---------------------------------------------------------------------------

class TestTC09010:
    """TC-09-010: variance_ratio = variance_after / variance_before.

    Note: window_values always starts with the anchor value (as per Module 06
    contract), so variance_after is computed on [anchor] + subsequent markers.
    The _compute helper uses anchor_val=301.0 (just above the 300% threshold)
    to produce realistic sequences.
    """

    def _compute(self, before_vals, after_vals, anchor_idx, anchor_val=301.0):
        """Build a minimal (visit, point) scenario and call compute_variance_indicators.

        window_values = [anchor_val] + after_vals, matching Module 06 contract.
        """
        from src.descent_window import DescentWindow
        from src.trigger_detection import TriggerResult
        seq = before_vals + [anchor_val] + after_vals
        sequences = {("V001", "P01"): seq}
        triggers = {
            ("V001", "P01"): TriggerResult(
                first_positive_marker="M_anchor",
                first_positive_index=anchor_idx,
                first_positive_value=anchor_val,
                no_cross_marker_effect=False,
            )
        }
        windows = {
            ("V001", "P01"): DescentWindow(
                window_values=[anchor_val] + after_vals,
                window_length=1 + len(after_vals),
                truncated_by_n_max=False,
            )
        }
        return compute_variance_indicators(sequences, triggers, windows)[("V001", "P01")]

    def test_ratio_computed_when_both_valid(self):
        # window=[301.0, 250.0, 200.0]; before=[100.0, 120.0]
        # ratio = var([301,250,200]) / var([100,120])
        import statistics as _s
        ind = self._compute([100.0, 120.0], [250.0, 200.0], anchor_idx=2)
        vb = _s.variance([100.0, 120.0])
        va = _s.variance([301.0, 250.0, 200.0])
        assert ind.variance_ratio == pytest.approx(va / vb)

    def test_ratio_none_when_before_is_none(self):
        # anchor at index 0 → no before segment → variance_before=None → ratio=None
        ind = self._compute([], [250.0, 200.0], anchor_idx=0)
        assert ind.variance_ratio is None

    def test_ratio_none_when_after_is_none(self):
        # window=[301.0] only → variance_after=None (single point) → ratio=None
        ind = self._compute([100.0, 120.0], [], anchor_idx=2)
        assert ind.variance_ratio is None

    def test_ratio_none_when_variance_before_zero(self):
        # all-equal before segment → variance=0.0 → ratio=None (avoid div-by-zero)
        ind = self._compute([200.0, 200.0], [250.0, 200.0], anchor_idx=2)
        assert ind.variance_ratio is None

    def test_ratio_greater_than_one_when_after_more_dispersed(self):
        # before very tight [100,101], window=[301, 50, 550] (wide) → ratio > 1
        ind = self._compute([100.0, 101.0], [50.0, 550.0], anchor_idx=2)
        assert ind.variance_ratio is not None
        assert ind.variance_ratio > 1.0

    def test_ratio_less_than_one_when_after_less_dispersed(self):
        # before very wide [1, 10000] → var ≈ 50M
        # window=[301.0, 300.5, 300.8] (extremely tight) → var ≈ 0.06 → ratio << 1
        ind = self._compute([1.0, 10000.0], [300.5, 300.8], anchor_idx=2)
        assert ind.variance_ratio is not None
        assert ind.variance_ratio < 1.0
