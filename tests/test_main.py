# LINKED-TO: [REQ-CPM-IA-P26.0001, REQ-CPM-IA-P26.0002, REQ-CPM-IA-P26.0003,
#              REQ-CPM-IA-P26.0004, REQ-CPM-IA-P26.0005, REQ-CPM-IA-P26.0006,
#              REQ-CPM-IA-P26.0007, REQ-CPM-IA-P26.0008, REQ-CPM-IA-P26.0009,
#              REQ-CPM-IA-P26.0010]
"""
Integration tests for src/main.py — Module 11: CPM-IA Pipeline Orchestrator.

Uses real mock data (data/input/raw_variation_mock.csv) with a temporary config
XML that redirects output to pytest's tmp_path. All test IDs trace to
.agent/modules/11_main.md (created post-session).

Mock data analysis (threshold_pct=300.0):
  V001/P01: M2=320.5 > 300 → first positive; window=[320.5,180.0,95.0]
  V001/P02: M2=410.0 > 300 → first positive; window=[410.0,350.0,120.0]
  V002/P01: M3=380.0 > 300 → first positive; window=[380.0,145.0]
  V002/P02: M2=330.0 > 300 → first positive; window=[330.0,275.0,190.0]
All 4 (visit, point) pairs are positive → no_cross_marker_effect=False for all.
"""

import sys
from pathlib import Path

import pytest

from src.config_loader import ConfigurationError
from src.main import main, run_pipeline

# Absolute path to the real mock CSV (relative to repo root)
MOCK_CSV = Path("data/input/raw_variation_mock.csv")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _write_temp_config(tmp_path: Path, mock_csv: Path = MOCK_CSV) -> Path:
    """Write a temporary XML config pointing at mock_csv and tmp_path/output."""
    output_dir = tmp_path / "output"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<cpm_ia_config>
    <input_path>{mock_csv.as_posix()}</input_path>
    <output_path>{output_dir.as_posix()}</output_path>
    <output_label_detail>cpm_ia_detail</output_label_detail>
    <output_label_aggregated>cpm_ia_aggregated</output_label_aggregated>
    <threshold_pct>300.0</threshold_pct>
    <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    <n_max>10</n_max>
</cpm_ia_config>"""
    config_path = tmp_path / "test_config.xml"
    config_path.write_text(xml, encoding="utf-8")
    return config_path


# ---------------------------------------------------------------------------
# TC-11-001 — Full end-to-end pipeline on mock data
# ---------------------------------------------------------------------------

class TestTC11001:
    """TC-11-001: Full pipeline on mock data -> 4 detail rows, 2 agg rows."""

    def test_detail_row_count(self, tmp_path):
        config_path = _write_temp_config(tmp_path)
        df_detail, _ = run_pipeline(config_path)
        assert len(df_detail) == 4  # 2 visits × 2 points

    def test_agg_row_count(self, tmp_path):
        config_path = _write_temp_config(tmp_path)
        _, df_agg = run_pipeline(config_path)
        assert len(df_agg) == 2  # 2 anatomical points

    def test_all_pairs_have_first_positive(self, tmp_path):
        # All 4 mock pairs exceed threshold_pct=300 → no_cross_marker_effect=False
        config_path = _write_temp_config(tmp_path)
        df_detail, _ = run_pipeline(config_path)
        assert (df_detail["no_cross_marker_effect"] == False).all()

    def test_agg_all_points_fully_positive(self, tmp_path):
        # Both points have 2 positive visits out of 2 total
        config_path = _write_temp_config(tmp_path)
        _, df_agg = run_pipeline(config_path)
        assert (df_agg["positive_visit_count"] == 2).all()
        assert (df_agg["total_visit_count"] == 2).all()
        assert all(abs(v - 1.0) < 1e-9 for v in df_agg["positive_prevalence"])

    def test_returns_dataframes(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        df_detail, df_agg = run_pipeline(config_path)
        assert isinstance(df_detail, pd.DataFrame)
        assert isinstance(df_agg, pd.DataFrame)


# ---------------------------------------------------------------------------
# TC-11-002 — Non-existent config path
# ---------------------------------------------------------------------------

class TestTC11002:
    """TC-11-002: Non-existent config path -> ConfigurationError raised."""

    def test_missing_config_raises(self, tmp_path):
        with pytest.raises(ConfigurationError):
            run_pipeline(tmp_path / "nonexistent.xml")


# ---------------------------------------------------------------------------
# TC-11-003 — Output CSV files written to configured path
# ---------------------------------------------------------------------------

class TestTC11003:
    """TC-11-003: After successful run, both CSV files exist at configured path."""

    def test_detail_csv_exists(self, tmp_path):
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        assert (tmp_path / "output" / "cpm_ia_detail.csv").exists()

    def test_agg_csv_exists(self, tmp_path):
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        assert (tmp_path / "output" / "cpm_ia_aggregated.csv").exists()

    def test_detail_csv_is_readable(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        df = pd.read_csv(tmp_path / "output" / "cpm_ia_detail.csv")
        assert len(df) == 4

    def test_agg_csv_is_readable(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        df = pd.read_csv(tmp_path / "output" / "cpm_ia_aggregated.csv")
        assert len(df) == 2


# ---------------------------------------------------------------------------
# TC-11-004 — main() exits 0 on success
# ---------------------------------------------------------------------------

class TestTC11004:
    """TC-11-004: main() with valid config -> SystemExit(0)."""

    def test_main_exits_zero(self, tmp_path, monkeypatch):
        config_path = _write_temp_config(tmp_path)
        monkeypatch.setattr(sys, "argv", ["main.py", str(config_path)])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


# ---------------------------------------------------------------------------
# TC-11-005 — main() exits 1 on missing argument
# ---------------------------------------------------------------------------

class TestTC11005:
    """TC-11-005: main() with no config argument -> SystemExit(1)."""

    def test_main_exits_one_no_arg(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["main.py"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_main_exits_one_bad_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["main.py", str(tmp_path / "missing.xml")])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
