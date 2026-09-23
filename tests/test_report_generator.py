# LINKED-TO: [REQ-CPM-IA-P26.0011]
"""Unit tests for src/report_generator.py — Module 11."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

import src.report_generator as rg
from src.config_loader import (
    CpmIaConfig, CsvInputConfig, DataQualityConfig, InputConfig,
)
from src.data_ingestion import DataQualityReport
from src.descent_window import DescentWindow
from src.positive_census import PointCensus
from src.report_generator import ReportError, _build_values, _escape, _fill_template, _fmt
from src.trigger_detection import Anchor, TriggerResult


def _make_config(tmp_path):
    return CpmIaConfig(
        input=InputConfig(
            type="csv",
            csv=CsvInputConfig(path=Path("data/input/test.csv")),
            excel=None, db=None,
        ),
        output_path=tmp_path,
        output_label_detail="cpm_ia_detail",
        output_label_aggregated="cpm_ia_aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=True),
    )


def _make_trigger(no_effect=False):
    if no_effect:
        return TriggerResult(anchors=[], positives_count=0, no_cross_marker_effect=True)
    anchor = Anchor(marker="M1", index=0, value=350.0)
    return TriggerResult(anchors=[anchor], positives_count=1, no_cross_marker_effect=False)


def _make_window(truncated=False):
    return DescentWindow(
        window_values=[350.0, 300.0, 250.0],
        window_length=3,
        truncated_by_n_max=truncated,
        window_close_reason="end",
    )


def _make_dq_report():
    return DataQualityReport(
        total_rows=10,
        rows_dropped_empty_keys=0,
        invalid_point_names=(),
        rows_affected_invalid_points=0,
        drop_mode=True,
    )


def _minimal_pipeline_inputs(tmp_path):
    df_detail = pd.DataFrame([
        {
            "visit_id": "V001", "visit_date": "2026-01-01", "point": "P01",
            "anchor_rank": 1, "anchor_marker": "M1", "anchor_value": 350.0,
            "anchor_index": 0, "positives_count": 1,
            "no_cross_marker_effect": False,
            "window_close_reason": "end",
        },
        {
            "visit_id": "V002", "visit_date": "2026-01-02", "point": "P01",
            "anchor_rank": None, "anchor_marker": None, "anchor_value": None,
            "anchor_index": None, "positives_count": 0,
            "no_cross_marker_effect": True,
            "window_close_reason": None,
        },
    ])
    df_agg = pd.DataFrame([{
        "point": "P01",
        "total_visit_count": 2,
        "positive_visit_count": 1,
        "positive_prevalence": 0.5,
        "median_descent_slope": -10.0,
        "median_descent_depth": 50.0,
        "median_descent_length": 3.0,
        "median_mean_per_step_decrease": 25.0,
    }])
    trigger_results = {
        ("V001", "P01"): _make_trigger(no_effect=False),
        ("V002", "P01"): _make_trigger(no_effect=True),
    }
    census = PointCensus(
        positive_point_count=1,
        positive_points=["P01"],
        total_point_count=1,
        total_positives_count=1,
    )
    descent_windows = {
        ("V001", "P01"): [_make_window(truncated=False)],
        ("V002", "P01"): [],
    }
    marker_orders = {"V001": ["M1", "M2"], "V002": ["M1"]}
    config = _make_config(tmp_path)
    run_dt = datetime(2026, 8, 31, 12, 0, 0)
    dq_report = _make_dq_report()
    return df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report


def _minimal_template():
    return (
        "__RUN_DATE__ __RUN_TIME__ __INPUT_PATH__ __OUTPUT_PATH__ "
        "__OUTPUT_LABEL_DETAIL__ __OUTPUT_LABEL_AGGREGATED__ "
        "__THRESHOLD_PCT__ __RISE_EPSILON__ __N_MAX__ "
        "__TOTAL_VISITS__ __TOTAL_POINTS__ __TOTAL_MARKERS__ __TOTAL_SERIES__ "
        "__POSITIVE_SERIES__ __NO_EFFECT_SERIES__ __POSITIVE_RATE__ __NO_EFFECT_RATE__ "
        "__POSITIVE_POINTS__ __NO_EFFECT_POINTS__ __TOTAL_POINT_COUNT__ "
        "__POSITIVE_POINTS_RATE__ __NO_EFFECT_POINTS_RATE__ "
        "__TRUNCATED_COUNT__ __TRUNCATED_RATE__ "
        "__TOTAL_ANCHORS__ __DQ_TOTAL_ROWS__ __DQ_DROPPED_EMPTY__ "
        "__DQ_INVALID_POINTS__ __DQ_INVALID_ROWS__ "
        "__AGG_TABLE_COUNTS__ __AGG_TABLE_MEDIANS__ __ANCHOR_TABLE_ROWS__"
    )


class TestTC11001:
    def test_ampersand(self):
        assert _escape("a&b") == r"a\&b"

    def test_percent(self):
        assert _escape("50%") == r"50\%"

    def test_dollar(self):
        assert _escape("$100") == "\\$100"

    def test_hash(self):
        assert _escape("#1") == "\\#1"

    def test_underscore(self):
        assert _escape("label_detail") == "label\\_detail"


class TestTC11002:
    def test_plain_string(self):
        assert _escape("hello world") == "hello world"

    def test_numeric_string(self):
        assert _escape("300.0") == "300.0"

    def test_integer_value(self):
        assert _escape(42) == "42"


class TestTC11003:
    def test_none_returns_dash(self):
        assert _fmt(None) == "---"


class TestTC11004:
    def test_float_nan(self):
        assert _fmt(float("nan")) == "---"


class TestTC11005:
    def test_positive_float(self):
        assert _fmt(3.14159) == "3.14"

    def test_negative_float(self):
        assert _fmt(-10.5) == "-10.50"


class TestTC11006:
    def test_one_decimal(self):
        assert _fmt(3.14159, decimals=1) == "3.1"


class TestTC11007:
    def test_single_replacement(self):
        assert _fill_template("Hello __NAME__!", {"NAME": "World"}) == "Hello World!"

    def test_multiple_replacements(self):
        result = _fill_template("__A__ and __B__", {"A": "alpha", "B": "beta"})
        assert result == "alpha and beta"


class TestTC11008:
    def test_extra_key_ignored(self):
        result = _fill_template("__A__", {"A": "alpha", "UNUSED": "gone"})
        assert result == "alpha"


_REQUIRED_KEYS = {
    "RUN_DATE", "RUN_TIME",
    "INPUT_PATH", "OUTPUT_PATH",
    "OUTPUT_LABEL_DETAIL", "OUTPUT_LABEL_AGGREGATED",
    "THRESHOLD_PCT", "RISE_EPSILON", "N_MAX",
    "TOTAL_VISITS", "TOTAL_POINTS", "TOTAL_MARKERS", "TOTAL_SERIES",
    "POSITIVE_SERIES", "NO_EFFECT_SERIES", "POSITIVE_RATE", "NO_EFFECT_RATE",
    "POSITIVE_POINTS", "NO_EFFECT_POINTS", "TOTAL_POINT_COUNT",
    "POSITIVE_POINTS_RATE", "NO_EFFECT_POINTS_RATE",
    "TRUNCATED_COUNT", "TRUNCATED_RATE",
    "TOTAL_ANCHORS", "DQ_TOTAL_ROWS", "DQ_DROPPED_EMPTY",
    "DQ_INVALID_POINTS", "DQ_INVALID_ROWS",
    "AGG_TABLE_COUNTS", "AGG_TABLE_MEDIANS", "ANCHOR_TABLE_ROWS",
}


class TestTC11009:
    def test_all_keys_present(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert _REQUIRED_KEYS.issubset(set(values.keys()))

    def test_run_date_format(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["RUN_DATE"] == "2026-08-31"

    def test_run_time_format(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["RUN_TIME"] == "12:00:00"

    def test_total_anchors_present(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["TOTAL_ANCHORS"] == "1"

    def test_dq_fields_present(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["DQ_TOTAL_ROWS"] == "10"
        assert values["DQ_DROPPED_EMPTY"] == "0"
        assert values["DQ_INVALID_POINTS"] == "0"
        assert values["DQ_INVALID_ROWS"] == "0"

    def test_all_values_are_strings(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        for k, v in values.items():
            assert isinstance(v, str), f"Key {k!r} has non-string value {v!r}"

    def test_input_path_uses_input_description(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert "test.csv" in values["INPUT_PATH"]


class TestTC11010:
    def test_missing_template_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", tmp_path / "nonexistent.tex.template")
        args = _minimal_pipeline_inputs(tmp_path)
        df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
        with pytest.raises(ReportError, match="template not found"):
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt, dq_report,
            )


class TestTC11011:
    def test_no_pdflatex_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        with patch("shutil.which", return_value=None):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            with pytest.raises(ReportError, match="pdflatex not found"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt, dq_report,
                )


class TestTC11012:
    def test_pdf_collision_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        (tmp_path / "cpm_ia_report.pdf").touch()

        with patch("shutil.which", return_value="/usr/bin/pdflatex"):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            with pytest.raises(ReportError, match="G-10"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt, dq_report,
                )


class TestTC11013:
    def _run_with_mock_pdflatex(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"

        def _fake(cmd, **kwargs):
            pdf_path.touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt, dq_report,
            )
        return (tmp_path / "cpm_ia_report.tex").read_text(encoding="utf-8")

    def test_tex_contains_run_date(self, tmp_path, monkeypatch):
        content = self._run_with_mock_pdflatex(tmp_path, monkeypatch)
        assert "2026-08-31" in content

    def test_tex_has_no_remaining_placeholders(self, tmp_path, monkeypatch):
        content = self._run_with_mock_pdflatex(tmp_path, monkeypatch)
        assert "__" not in content


class TestTC11014:
    def test_pdflatex_called_twice(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"
        call_count = {"n": 0}

        def _fake(cmd, **kwargs):
            call_count["n"] += 1
            pdf_path.touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt, dq_report,
            )

        assert call_count["n"] == 2


class TestTC11016:
    def test_returns_pdf_path(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"

        def _fake(cmd, **kwargs):
            pdf_path.touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            result = rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt, dq_report,
            )

        assert result == pdf_path
        assert result.exists()


class TestTC11017:
    def test_pdflatex_nonzero_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _fail(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, stdout="Fatal error", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_fail):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            with pytest.raises(ReportError, match="pdflatex failed"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt, dq_report,
                )

    def test_tex_preserved_on_failure(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _fail(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, stdout="error", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_fail):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            with pytest.raises(ReportError):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt, dq_report,
                )

        assert (tmp_path / "cpm_ia_report.tex").exists()


class TestTC11018:
    def test_pdf_absent_after_compilation_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _ok_no_pdf(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"), \
             patch("subprocess.run", side_effect=_ok_no_pdf):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt, dq_report = args
            with pytest.raises(ReportError, match="PDF not found after compilation"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt, dq_report,
                )
