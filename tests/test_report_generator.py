# LINKED-TO: [REQ-CPM-IA-P26.0011]
"""
Unit tests for src/report_generator.py — Module 11: Automated PDF Run Report.

All test IDs trace to .agent/modules/11_report_generator.md.
"""

from __future__ import annotations

import math
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest

import src.report_generator as rg
from src.config_loader import CpmIaConfig
from src.descent_window import DescentWindow
from src.positive_census import PointCensus
from src.report_generator import ReportError, _build_values, _escape, _fill_template, _fmt
from src.trigger_detection import TriggerResult


# ---------------------------------------------------------------------------
# Shared fixture builders
# ---------------------------------------------------------------------------

def _make_config(tmp_path: Path) -> CpmIaConfig:
    return CpmIaConfig(
        input_path=Path("data/input/test.csv"),
        output_path=tmp_path,
        output_label_detail="cpm_ia_detail",
        output_label_aggregated="cpm_ia_aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
    )


def _make_trigger(no_effect: bool = False) -> TriggerResult:
    if no_effect:
        return TriggerResult(
            first_positive_marker=None,
            first_positive_index=None,
            first_positive_value=None,
            no_cross_marker_effect=True,
        )
    return TriggerResult(
        first_positive_marker="M1",
        first_positive_index=0,
        first_positive_value=350.0,
        no_cross_marker_effect=False,
    )


def _make_window(truncated: bool = False) -> DescentWindow:
    return DescentWindow(
        window_values=[350.0, 300.0, 250.0],
        window_length=3,
        truncated_by_n_max=truncated,
    )


def _minimal_pipeline_inputs(tmp_path: Path):
    """Return the full set of inputs required by _build_values / generate_report."""
    df_detail = pd.DataFrame([
        {
            "visit_id": "V001", "visit_date": "2026-01-01", "point": "P01",
            "first_positive_marker": "M1", "first_positive_value": 350.0,
            "no_cross_marker_effect": False,
        },
        {
            "visit_id": "V002", "visit_date": "2026-01-02", "point": "P01",
            "first_positive_marker": None, "first_positive_value": None,
            "no_cross_marker_effect": True,
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
    )
    descent_windows = {
        ("V001", "P01"): _make_window(truncated=False),
        ("V002", "P01"): None,
    }
    marker_orders = {"V001": ["M1", "M2"], "V002": ["M1"]}
    config = _make_config(tmp_path)
    run_dt = datetime(2026, 8, 31, 12, 0, 0)
    return df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt


def _minimal_template() -> str:
    """Minimal LaTeX template containing all placeholders used by _build_values."""
    return (
        "__RUN_DATE__ __RUN_TIME__ __INPUT_PATH__ __OUTPUT_PATH__ "
        "__OUTPUT_LABEL_DETAIL__ __OUTPUT_LABEL_AGGREGATED__ "
        "__THRESHOLD_PCT__ __RISE_EPSILON__ __N_MAX__ "
        "__TOTAL_VISITS__ __TOTAL_POINTS__ __TOTAL_MARKERS__ __TOTAL_SERIES__ "
        "__POSITIVE_SERIES__ __NO_EFFECT_SERIES__ __POSITIVE_RATE__ __NO_EFFECT_RATE__ "
        "__POSITIVE_POINTS__ __NO_EFFECT_POINTS__ __TOTAL_POINT_COUNT__ "
        "__POSITIVE_POINTS_RATE__ __NO_EFFECT_POINTS_RATE__ "
        "__TRUNCATED_COUNT__ __TRUNCATED_RATE__ "
        "__AGG_TABLE_COUNTS__ __AGG_TABLE_MEDIANS__ __ANCHOR_TABLE_ROWS__"
    )


# ---------------------------------------------------------------------------
# TC-11-001 — _escape: special characters
# ---------------------------------------------------------------------------

class TestTC11001:
    """TC-11-001: _escape translates LaTeX special characters correctly."""

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

    def test_braces(self):
        assert _escape("{x}") == "\\{x\\}"

    def test_tilde(self):
        assert _escape("a~b") == "a\\textasciitilde{}b"

    def test_caret(self):
        assert _escape("a^b") == "a\\textasciicircum{}b"

    def test_backslash(self):
        assert _escape("a\\b") == "a\\textbackslash{}b"

    def test_combined(self):
        result = _escape("50% & $100")
        assert "\\%" in result
        assert "\\&" in result
        assert "\\$" in result


# ---------------------------------------------------------------------------
# TC-11-002 — _escape: passthrough on clean strings
# ---------------------------------------------------------------------------

class TestTC11002:
    """TC-11-002: _escape leaves strings with no special characters unchanged."""

    def test_plain_string(self):
        assert _escape("hello world") == "hello world"

    def test_path_with_slashes(self):
        result = _escape("/data/output/cpm")
        assert result == "/data/output/cpm"

    def test_numeric_string(self):
        assert _escape("300.0") == "300.0"

    def test_integer_value(self):
        assert _escape(42) == "42"


# ---------------------------------------------------------------------------
# TC-11-003 — _fmt: None -> "---"
# ---------------------------------------------------------------------------

class TestTC11003:
    """TC-11-003: _fmt returns '---' for None."""

    def test_none_returns_dash(self):
        assert _fmt(None) == "---"

    def test_none_with_decimals_arg(self):
        assert _fmt(None, decimals=1) == "---"


# ---------------------------------------------------------------------------
# TC-11-004 — _fmt: NaN -> "---"
# ---------------------------------------------------------------------------

class TestTC11004:
    """TC-11-004: _fmt returns '---' for float NaN."""

    def test_float_nan(self):
        assert _fmt(float("nan")) == "---"

    def test_none_vs_nan_same_output(self):
        assert _fmt(None) == _fmt(float("nan"))


# ---------------------------------------------------------------------------
# TC-11-005 — _fmt: valid float with default 2 decimals
# ---------------------------------------------------------------------------

class TestTC11005:
    """TC-11-005: _fmt formats float values to fixed-point strings."""

    def test_positive_float(self):
        assert _fmt(3.14159) == "3.14"

    def test_negative_float(self):
        assert _fmt(-10.5) == "-10.50"

    def test_integer_cast(self):
        assert _fmt(5) == "5.00"

    def test_zero(self):
        assert _fmt(0.0) == "0.00"


# ---------------------------------------------------------------------------
# TC-11-006 — _fmt: custom decimals
# ---------------------------------------------------------------------------

class TestTC11006:
    """TC-11-006: _fmt respects the decimals parameter."""

    def test_one_decimal(self):
        assert _fmt(3.14159, decimals=1) == "3.1"

    def test_zero_decimals(self):
        assert _fmt(3.7, decimals=0) == "4"

    def test_four_decimals(self):
        assert _fmt(1.23456789, decimals=4) == "1.2346"


# ---------------------------------------------------------------------------
# TC-11-007 — _fill_template: all placeholders replaced
# ---------------------------------------------------------------------------

class TestTC11007:
    """TC-11-007: _fill_template replaces every __KEY__ in the template."""

    def test_single_replacement(self):
        result = _fill_template("Hello __NAME__!", {"NAME": "World"})
        assert result == "Hello World!"

    def test_multiple_replacements(self):
        tpl = "__A__ and __B__"
        result = _fill_template(tpl, {"A": "alpha", "B": "beta"})
        assert result == "alpha and beta"

    def test_all_occurrences_replaced(self):
        tpl = "__K__ __K__ __K__"
        result = _fill_template(tpl, {"K": "x"})
        assert result == "x x x"

    def test_empty_values_dict_returns_template_unchanged(self):
        tpl = "no placeholders here"
        assert _fill_template(tpl, {}) == tpl


# ---------------------------------------------------------------------------
# TC-11-008 — _fill_template: unknown keys silently ignored
# ---------------------------------------------------------------------------

class TestTC11008:
    """TC-11-008: _fill_template does not raise when a key is absent from template."""

    def test_extra_key_ignored(self):
        tpl = "__A__"
        result = _fill_template(tpl, {"A": "alpha", "UNUSED": "gone"})
        assert result == "alpha"

    def test_missing_placeholder_stays_in_output(self):
        tpl = "__A__ __B__"
        result = _fill_template(tpl, {"A": "alpha"})
        assert "__B__" in result


# ---------------------------------------------------------------------------
# TC-11-009 — _build_values: required keys present
# ---------------------------------------------------------------------------

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
    "AGG_TABLE_COUNTS", "AGG_TABLE_MEDIANS", "ANCHOR_TABLE_ROWS",
}


class TestTC11009:
    """TC-11-009: _build_values returns a dict with all required placeholder keys."""

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

    def test_positive_series_count(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["POSITIVE_SERIES"] == "1"
        assert values["NO_EFFECT_SERIES"] == "1"
        assert values["TOTAL_SERIES"] == "2"

    def test_truncated_count_zero_when_no_truncation(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        assert values["TRUNCATED_COUNT"] == "0"

    def test_all_values_are_strings(self, tmp_path):
        args = _minimal_pipeline_inputs(tmp_path)
        values = _build_values(*args)
        for k, v in values.items():
            assert isinstance(v, str), f"Key {k!r} has non-string value {v!r}"


# ---------------------------------------------------------------------------
# TC-11-010 — generate_report: template missing raises ReportError
# ---------------------------------------------------------------------------

class TestTC11010:
    """TC-11-010: generate_report raises ReportError when LaTeX template is absent."""

    def test_missing_template_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", tmp_path / "nonexistent.tex.template")
        args = _minimal_pipeline_inputs(tmp_path)
        df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
        with pytest.raises(ReportError, match="template not found"):
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt,
            )


# ---------------------------------------------------------------------------
# TC-11-011 — generate_report: pdflatex not on PATH raises ReportError
# ---------------------------------------------------------------------------

class TestTC11011:
    """TC-11-011: generate_report raises ReportError when pdflatex is absent from PATH."""

    def test_no_pdflatex_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        with patch("shutil.which", return_value=None):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            with pytest.raises(ReportError, match="pdflatex not found"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt,
                )


# ---------------------------------------------------------------------------
# TC-11-012 — generate_report: G-10 PDF already exists raises ReportError
# ---------------------------------------------------------------------------

class TestTC11012:
    """TC-11-012: generate_report raises ReportError when the output PDF already exists (G-10)."""

    def test_pdf_collision_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        (tmp_path / "cpm_ia_report.pdf").touch()

        with patch("shutil.which", return_value="/usr/bin/pdflatex"):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            with pytest.raises(ReportError, match="G-10"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt,
                )


# ---------------------------------------------------------------------------
# TC-11-013 — generate_report: .tex written with filled content
# ---------------------------------------------------------------------------

class TestTC11013:
    """TC-11-013: generate_report writes a .tex file with all placeholders replaced."""

    def _run_with_mock_pdflatex(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"

        def _fake(cmd, **kwargs):
            pdf_path.touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt,
            )
        return (tmp_path / "cpm_ia_report.tex").read_text(encoding="utf-8")

    def test_tex_contains_run_date(self, tmp_path, monkeypatch):
        content = self._run_with_mock_pdflatex(tmp_path, monkeypatch)
        assert "2026-08-31" in content

    def test_tex_has_no_remaining_placeholders(self, tmp_path, monkeypatch):
        content = self._run_with_mock_pdflatex(tmp_path, monkeypatch)
        assert "__" not in content


# ---------------------------------------------------------------------------
# TC-11-014 — generate_report: pdflatex called exactly twice
# ---------------------------------------------------------------------------

class TestTC11014:
    """TC-11-014: generate_report invokes pdflatex exactly twice (TOC pass)."""

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

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt,
            )

        assert call_count["n"] == 2


# ---------------------------------------------------------------------------
# TC-11-015 — generate_report: aux files removed after compilation
# ---------------------------------------------------------------------------

class TestTC11015:
    """TC-11-015: generate_report removes .aux/.log/.out/.toc after compilation."""

    def test_aux_files_deleted(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"

        def _fake(cmd, **kwargs):
            pdf_path.touch()
            for ext in (".aux", ".log", ".out", ".toc"):
                (tmp_path / f"cpm_ia_report{ext}").touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt,
            )

        for ext in (".aux", ".log", ".out", ".toc"):
            assert not (tmp_path / f"cpm_ia_report{ext}").exists(),                 f"Aux file {ext} was not removed"


# ---------------------------------------------------------------------------
# TC-11-016 — generate_report: returns pdf_path on success
# ---------------------------------------------------------------------------

class TestTC11016:
    """TC-11-016: generate_report returns the Path of the compiled PDF."""

    def test_returns_pdf_path(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)
        pdf_path = tmp_path / "cpm_ia_report.pdf"

        def _fake(cmd, **kwargs):
            pdf_path.touch()
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fake):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            result = rg.generate_report(
                df_detail, df_agg, trigger_results, census,
                descent_windows, marker_orders, config, run_dt,
            )

        assert result == pdf_path
        assert result.exists()


# ---------------------------------------------------------------------------
# TC-11-017 — generate_report: pdflatex failure raises ReportError
# ---------------------------------------------------------------------------

class TestTC11017:
    """TC-11-017: generate_report raises ReportError when pdflatex exits non-zero."""

    def test_pdflatex_nonzero_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _fail(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, stdout="Fatal error", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fail):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            with pytest.raises(ReportError, match="pdflatex failed"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt,
                )

    def test_tex_preserved_on_failure(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _fail(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, stdout="error", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_fail):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            with pytest.raises(ReportError):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt,
                )

        assert (tmp_path / "cpm_ia_report.tex").exists(), ".tex must be preserved on failure"


# ---------------------------------------------------------------------------
# TC-11-018 — generate_report: PDF absent after pdflatex exit 0 raises ReportError
# ---------------------------------------------------------------------------

class TestTC11018:
    """TC-11-018: generate_report raises ReportError when PDF is missing after compilation."""

    def test_pdf_absent_after_compilation_raises(self, tmp_path, monkeypatch):
        fake_template = tmp_path / "cpm_ia_report.tex.template"
        fake_template.write_text(_minimal_template(), encoding="utf-8")
        monkeypatch.setattr(rg, "_TEMPLATE_PATH", fake_template)

        def _ok_no_pdf(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch("shutil.which", return_value="/usr/bin/pdflatex"),              patch("subprocess.run", side_effect=_ok_no_pdf):
            args = _minimal_pipeline_inputs(tmp_path)
            df_detail, df_agg, trigger_results, census, descent_windows, marker_orders, config, run_dt = args
            with pytest.raises(ReportError, match="PDF not found after compilation"):
                rg.generate_report(
                    df_detail, df_agg, trigger_results, census,
                    descent_windows, marker_orders, config, run_dt,
                )
