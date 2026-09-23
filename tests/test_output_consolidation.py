# LINKED-TO: [REQ-CPM-IA-P26.0010]
"""Unit tests for src/output_consolidation.py — Module 10."""

from pathlib import Path

import pandas as pd
import pytest

from src.config_loader import (
    CpmIaConfig, CsvInputConfig, DataQualityConfig, InputConfig,
)
from src.descent_descriptors import DescentDescriptor
from src.descent_window import DescentWindow
from src.output_consolidation import OutputError, consolidate_outputs
from src.positive_census import PointCensus
from src.trigger_detection import Anchor, TriggerResult
from src.variance_indicator import VarianceIndicator


def _make_config(tmp_path, label_detail="detail", label_agg="aggregated"):
    return CpmIaConfig(
        input=InputConfig(
            type="csv",
            csv=CsvInputConfig(path=Path("data/input/raw_variation_mock.csv")),
            excel=None, db=None,
        ),
        output_path=tmp_path,
        output_label_detail=label_detail,
        output_label_aggregated=label_agg,
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=True),
    )


def _make_trigger_single(anchor_idx, anchor_val, marker="M2", no_effect=False):
    if no_effect:
        return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)
    anchor = Anchor(marker=marker, index=anchor_idx, value=anchor_val)
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


def _make_window(values, close_reason="end"):
    return DescentWindow(
        window_values=values, window_length=len(values),
        truncated_by_n_max=False, window_close_reason=close_reason,
    )


def _make_descriptor(depth, length, mpsd):
    return DescentDescriptor(descent_depth=depth, descent_length=length, mean_per_step_decrease=mpsd)


def _make_variance(vb, va):
    vr = (va / vb) if (vb is not None and va is not None and vb > 0) else None
    return VarianceIndicator(variance_before=vb, variance_after=va, variance_ratio=vr)


def _base_inputs(tmp_path):
    """
    2 visits x 2 points — all single-anchor:
      V001/P01 — positive (anchor M2, val=350, window=[350,300,250])
      V001/P02 — positive (anchor M1, val=400, window=[400,350])
      V002/P01 — positive (anchor M2, val=320, window=[320,270,220])
      V002/P02 — no_cross_marker_effect=True
    """
    df_raw = pd.DataFrame([
        {"visit_id": "V001", "marker": "M1", "point": "P01", "percentage_variation": 100.0, "visit_date": "2026-01-01"},
        {"visit_id": "V001", "marker": "M2", "point": "P01", "percentage_variation": 350.0, "visit_date": "2026-01-01"},
        {"visit_id": "V001", "marker": "M1", "point": "P02", "percentage_variation": 400.0, "visit_date": "2026-01-01"},
        {"visit_id": "V001", "marker": "M2", "point": "P02", "percentage_variation": 200.0, "visit_date": "2026-01-01"},
        {"visit_id": "V002", "marker": "M1", "point": "P01", "percentage_variation": 150.0, "visit_date": "2026-02-01"},
        {"visit_id": "V002", "marker": "M2", "point": "P01", "percentage_variation": 320.0, "visit_date": "2026-02-01"},
        {"visit_id": "V002", "marker": "M1", "point": "P02", "percentage_variation": 200.0, "visit_date": "2026-02-01"},
        {"visit_id": "V002", "marker": "M2", "point": "P02", "percentage_variation": 220.0, "visit_date": "2026-02-01"},
    ])

    trigger_results = {
        ("V001", "P01"): _make_trigger_single(1, 350.0),
        ("V001", "P02"): _make_trigger_single(0, 400.0, marker="M1"),
        ("V002", "P01"): _make_trigger_single(1, 320.0),
        ("V002", "P02"): _make_trigger_single(None, None, no_effect=True),
    }

    descent_windows = {
        ("V001", "P01"): [_make_window([350.0, 300.0, 250.0])],
        ("V001", "P02"): [_make_window([400.0, 350.0])],
        ("V002", "P01"): [_make_window([320.0, 270.0, 220.0])],
        ("V002", "P02"): [],
    }

    slopes = {
        ("V001", "P01"): [-50.0],
        ("V001", "P02"): [-50.0],
        ("V002", "P01"): [-50.0],
        ("V002", "P02"): [],
    }

    descriptors = {
        ("V001", "P01"): [_make_descriptor(100.0, 3, 50.0)],
        ("V001", "P02"): [_make_descriptor(50.0, 2, 50.0)],
        ("V002", "P01"): [_make_descriptor(100.0, 3, 50.0)],
        ("V002", "P02"): [],
    }

    variance_indicators = {
        ("V001", "P01"): [_make_variance(200.0, 2500.0)],
        ("V001", "P02"): [None],
        ("V002", "P01"): [_make_variance(None, 2500.0)],
        ("V002", "P02"): [],
    }

    census = PointCensus(
        positive_point_count=2,
        positive_points=["P01", "P02"],
        total_point_count=2,
        total_positives_count=3,
    )

    config = _make_config(tmp_path)
    return df_raw, trigger_results, census, descent_windows, slopes, descriptors, variance_indicators, config


class TestTC10001:
    """TC-10-001: 2 visits x 2 points, 3 positive anchors + 1 no-effect -> detail=4 rows."""

    def test_detail_row_count(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        assert len(df_detail) == 4  # one row per (visit, point) since all single-anchor

    def test_agg_row_count(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        assert len(df_agg) == 2

    def test_csv_files_written(self, tmp_path):
        args = _base_inputs(tmp_path)
        consolidate_outputs(*args)
        assert (tmp_path / "detail.csv").exists()
        assert (tmp_path / "aggregated.csv").exists()

    def test_detail_csv_row_count(self, tmp_path):
        args = _base_inputs(tmp_path)
        consolidate_outputs(*args)
        df = pd.read_csv(tmp_path / "detail.csv")
        assert len(df) == 4


class TestTC10002:
    """TC-10-002: One no-effect row -> anchor_marker=None, metrics NaN."""

    def test_no_effect_row_present(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        row = df_detail[(df_detail["visit_id"] == "V002") & (df_detail["point"] == "P02")]
        assert len(row) == 1

    def test_no_effect_anchor_marker_none(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        row = df_detail[(df_detail["visit_id"] == "V002") & (df_detail["point"] == "P02")]
        assert row["anchor_marker"].isna().all()

    def test_no_effect_flag_true(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        row = df_detail[(df_detail["visit_id"] == "V002") & (df_detail["point"] == "P02")]
        assert bool(row["no_cross_marker_effect"].iloc[0]) is True

    def test_no_effect_metrics_nan(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        row = df_detail[(df_detail["visit_id"] == "V002") & (df_detail["point"] == "P02")]
        for col in ("descent_slope", "descent_depth", "descent_length", "mean_per_step_decrease", "variance_ratio"):
            assert pd.isna(row[col].iloc[0]), f"{col} should be NaN for no-effect row"


class TestTC10003:
    """TC-10-003: Output file already exists -> raises OutputError."""

    def test_detail_file_exists_raises(self, tmp_path):
        (tmp_path / "detail.csv").touch()
        args = _base_inputs(tmp_path)
        with pytest.raises(OutputError, match="already exists"):
            consolidate_outputs(*args)

    def test_agg_file_exists_raises(self, tmp_path):
        (tmp_path / "aggregated.csv").touch()
        args = _base_inputs(tmp_path)
        with pytest.raises(OutputError, match="already exists"):
            consolidate_outputs(*args)


class TestTC10004:
    """TC-10-004: Aggregation medians match manual calculation."""

    def test_p01_median_descent_slope(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P01"]
        assert row["median_descent_slope"].iloc[0] == pytest.approx(-50.0)

    def test_p01_median_descent_depth(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P01"]
        assert row["median_descent_depth"].iloc[0] == pytest.approx(100.0)

    def test_p02_only_positive_visit_contributes(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P02"]
        assert row["median_descent_depth"].iloc[0] == pytest.approx(50.0)

    def test_p02_positive_visit_count(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P02"]
        assert int(row["positive_visit_count"].iloc[0]) == 1

    def test_p01_positive_prevalence(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P01"]
        assert row["positive_prevalence"].iloc[0] == pytest.approx(1.0)

    def test_p02_positive_prevalence(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        row = df_agg[df_agg["point"] == "P02"]
        assert row["positive_prevalence"].iloc[0] == pytest.approx(0.5)


class TestTC10005:
    """TC-10-005: Duplicate (visit, point) metadata raises OutputError (G-09)."""

    def test_conflicting_metadata_raises(self, tmp_path):
        df_raw, trigger_results, census, descent_windows, slopes, descriptors, var_inds, config = (
            _base_inputs(tmp_path)
        )
        df_raw = df_raw.copy()
        df_raw.loc[
            (df_raw["visit_id"] == "V001") & (df_raw["marker"] == "M2") & (df_raw["point"] == "P01"),
            "visit_date"
        ] = "9999-12-31"
        with pytest.raises(OutputError):
            consolidate_outputs(
                df_raw, trigger_results, census, descent_windows,
                slopes, descriptors, var_inds, config
            )


class TestTC10006:
    """TC-10-006: Output path does not exist -> directory created."""

    def test_missing_dir_is_created(self, tmp_path):
        new_dir = tmp_path / "subdir" / "output"
        assert not new_dir.exists()
        df_raw, trigger_results, census, descent_windows, slopes, descriptors, var_inds, _ = (
            _base_inputs(tmp_path)
        )
        config = CpmIaConfig(
            input=InputConfig(
                type="csv",
                csv=CsvInputConfig(path=Path("data/input/raw_variation_mock.csv")),
                excel=None, db=None,
            ),
            output_path=new_dir,
            output_label_detail="detail",
            output_label_aggregated="aggregated",
            threshold_pct=300.0,
            rise_tolerance_epsilon=5.0,
            n_max=10,
            data_quality=DataQualityConfig(drop_invalid_points=True),
        )
        consolidate_outputs(
            df_raw, trigger_results, census, descent_windows,
            slopes, descriptors, var_inds, config
        )
        assert new_dir.exists()
        assert (new_dir / "detail.csv").exists()


class TestTC10007:
    """TC-10-007: All no_cross_marker_effect=True -> metrics NaN."""

    def _all_no_effect_inputs(self, tmp_path):
        df_raw = pd.DataFrame([
            {"visit_id": "V001", "marker": "M1", "point": "P01",
             "percentage_variation": 100.0, "visit_date": "2026-01-01"},
            {"visit_id": "V002", "marker": "M1", "point": "P01",
             "percentage_variation": 150.0, "visit_date": "2026-02-01"},
        ])
        trigger_results = {
            ("V001", "P01"): _make_trigger_single(None, None, no_effect=True),
            ("V002", "P01"): _make_trigger_single(None, None, no_effect=True),
        }
        descent_windows  = {("V001", "P01"): [], ("V002", "P01"): []}
        slopes           = {("V001", "P01"): [], ("V002", "P01"): []}
        descriptors      = {("V001", "P01"): [], ("V002", "P01"): []}
        var_inds         = {("V001", "P01"): [], ("V002", "P01"): []}
        census = PointCensus(
            positive_point_count=0, positive_points=[], total_point_count=1,
            total_positives_count=0,
        )
        config = _make_config(tmp_path)
        return df_raw, trigger_results, census, descent_windows, slopes, descriptors, var_inds, config

    def test_detail_all_metrics_nan(self, tmp_path):
        args = self._all_no_effect_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        for col in ("descent_slope", "descent_depth"):
            assert df_detail[col].isna().all()

    def test_agg_positive_visit_count_zero(self, tmp_path):
        args = self._all_no_effect_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        assert (df_agg["positive_visit_count"] == 0).all()

    def test_agg_prevalence_zero(self, tmp_path):
        args = self._all_no_effect_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        assert (df_agg["positive_prevalence"] == 0.0).all()


class TestTC10008:
    """TC-10-008: Detail CSV contains expected columns (new schema)."""

    EXPECTED_DETAIL_COLS = {
        "visit_id", "visit_date", "point",
        "anchor_rank", "anchor_marker", "anchor_value", "anchor_index",
        "positives_count", "no_cross_marker_effect",
        "descent_slope", "descent_depth", "descent_length", "mean_per_step_decrease",
        "window_close_reason",
        "variance_before", "variance_after", "variance_ratio",
    }
    EXPECTED_AGG_COLS = {
        "point", "total_visit_count", "positive_visit_count", "positive_prevalence",
        "median_positives_count",
        "median_descent_slope", "median_descent_depth", "median_descent_length",
        "median_mean_per_step_decrease",
    }

    def test_detail_columns(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        assert set(df_detail.columns) == self.EXPECTED_DETAIL_COLS

    def test_agg_columns(self, tmp_path):
        args = _base_inputs(tmp_path)
        _, df_agg = consolidate_outputs(*args)
        assert set(df_agg.columns) == self.EXPECTED_AGG_COLS


class TestTC10009:
    """TC-10-009: Multi-anchor series produces multiple rows per (visit, point)."""

    def test_two_anchors_two_rows(self, tmp_path):
        """Visit V001/P01 has 2 anchors -> 2 rows in detail."""
        from src.trigger_detection import Anchor, TriggerResult
        df_raw = pd.DataFrame([
            {"visit_id": "V001", "marker": "M1", "point": "P01", "percentage_variation": 350.0, "visit_date": "2026-01-01"},
            {"visit_id": "V001", "marker": "M2", "point": "P01", "percentage_variation": 200.0, "visit_date": "2026-01-01"},
            {"visit_id": "V001", "marker": "M3", "point": "P01", "percentage_variation": 400.0, "visit_date": "2026-01-01"},
        ])
        a0 = Anchor(marker="M1", index=0, value=350.0)
        a1 = Anchor(marker="M3", index=2, value=400.0)
        trigger = TriggerResult(anchors=[a0, a1], positives_count=2, no_cross_marker_effect=False)
        trigger_results = {("V001", "P01"): trigger}
        descent_windows = {
            ("V001", "P01"): [
                _make_window([350.0, 200.0]),
                _make_window([400.0]),
            ]
        }
        slopes = {("V001", "P01"): [-150.0, None]}
        descriptors = {
            ("V001", "P01"): [
                _make_descriptor(150.0, 2, 150.0),
                _make_descriptor(0.0, 1, 0.0),
            ]
        }
        variance_indicators = {("V001", "P01"): [None, None]}
        census = PointCensus(
            positive_point_count=1, positive_points=["P01"],
            total_point_count=1, total_positives_count=2,
        )
        config = _make_config(tmp_path)
        df_detail, df_agg = consolidate_outputs(
            df_raw, trigger_results, census, descent_windows,
            slopes, descriptors, variance_indicators, config
        )
        p01_rows = df_detail[df_detail["point"] == "P01"]
        assert len(p01_rows) == 2
        assert set(p01_rows["anchor_rank"]) == {1, 2}
        assert set(p01_rows["anchor_marker"]) == {"M1", "M3"}


class TestTC10010:
    """TC-10-010: G-09 uniqueness by (visit_id, point, anchor_marker)."""

    def test_no_effect_row_unique(self, tmp_path):
        args = _base_inputs(tmp_path)
        df_detail, _ = consolidate_outputs(*args)
        # no_effect rows have anchor_marker=None; should be unique per (visit, point)
        no_eff = df_detail[df_detail["no_cross_marker_effect"]]
        assert len(no_eff) == no_eff[["visit_id", "point"]].drop_duplicates().shape[0]
