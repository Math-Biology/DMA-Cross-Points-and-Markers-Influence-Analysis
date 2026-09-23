# LINKED-TO: [REQ-CPM-IA-P26.0001, REQ-CPM-IA-P26.0002, REQ-CPM-IA-P26.0003,
#              REQ-CPM-IA-P26.0004, REQ-CPM-IA-P26.0005, REQ-CPM-IA-P26.0006,
#              REQ-CPM-IA-P26.0007, REQ-CPM-IA-P26.0008, REQ-CPM-IA-P26.0009,
#              REQ-CPM-IA-P26.0010]
"""
Integration tests for src/main.py — CPM-IA Pipeline Orchestrator.

Uses inline mock CSV data (written to tmp_path) to avoid dependency on deleted
data/input/ CSV files. All (visit, point) pairs exceed threshold_pct=300 in the
mock, so all series are positive.

Mock data layout (threshold_pct=300.0, inclusive >=):
  V001/P01: M1=100, M2=320.5, M3=180.0, M4=95.0  → 1 anchor (M2)
  V001/P02: M1=50,  M2=410.0, M3=350.0, M4=120.0 → 2 anchors (M2, M3)
  V002/P01: M1=200, M2=150.0, M3=380.0, M4=145.0 → 1 anchor (M3)
  V002/P02: M1=80,  M2=330.0, M3=275.0, M4=190.0 → 1 anchor (M2)

Detail row count: 1+2+1+1 = 5 rows; agg row count: 2 points (P01, P02).
"""

import sys
from pathlib import Path

import pytest

from src.config_loader import ConfigurationError
from src.main import main, run_pipeline

# ---------------------------------------------------------------------------
# Mock CSV content — inline, no dependency on deleted data/input/ CSV files
# ---------------------------------------------------------------------------
# visit_id,marker,point,percentage_variation,visit_date
_MOCK_CSV_CONTENT = """visit_id,marker,point,percentage_variation,visit_date
V001,M1,LH - 1 - a - P01,100.0,2026-01-01
V001,M2,LH - 1 - a - P01,320.5,2026-01-01
V001,M3,LH - 1 - a - P01,180.0,2026-01-01
V001,M4,LH - 1 - a - P01,95.0,2026-01-01
V001,M1,LH - 1 - a - P02,50.0,2026-01-01
V001,M2,LH - 1 - a - P02,410.0,2026-01-01
V001,M3,LH - 1 - a - P02,350.0,2026-01-01
V001,M4,LH - 1 - a - P02,120.0,2026-01-01
V002,M1,LH - 1 - a - P01,200.0,2026-02-01
V002,M2,LH - 1 - a - P01,150.0,2026-02-01
V002,M3,LH - 1 - a - P01,380.0,2026-02-01
V002,M4,LH - 1 - a - P01,145.0,2026-02-01
V002,M1,LH - 1 - a - P02,80.0,2026-02-01
V002,M2,LH - 1 - a - P02,330.0,2026-02-01
V002,M3,LH - 1 - a - P02,275.0,2026-02-01
V002,M4,LH - 1 - a - P02,190.0,2026-02-01
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _write_temp_config(tmp_path: Path) -> Path:
    """Write mock CSV and a temporary XML config pointing at it."""
    # Write inline mock data to tmp file
    mock_csv = tmp_path / "mock_data.csv"
    mock_csv.write_text(_MOCK_CSV_CONTENT.strip(), encoding="utf-8")

    output_dir = tmp_path / "output"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<cpm_ia_config>
    <input_path>{mock_csv.as_posix()}</input_path>
    <output_path>{output_dir.as_posix()}</output_path>
    <output_label_detail>cpm_ia_detail</output_label_detail>
    <output_label_aggregated>cpm_ia_aggregated</output_label_aggregated>
    <threshold_pct>300.0</threshold_pct>
    <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    <n_max>1000</n_max>
</cpm_ia_config>"""
    config_path = tmp_path / "test_config.xml"
    config_path.write_text(xml, encoding="utf-8")
    return config_path


# ---------------------------------------------------------------------------
# TC-11-001 — Full end-to-end pipeline on mock data
# ---------------------------------------------------------------------------

class TestTC11001:
    """TC-11-001: Full pipeline on mock data; validate detail and agg row counts."""

    def test_detail_row_count(self, tmp_path):
        # 5 anchor rows: P01 has 1+1=2 visits with 1 anchor each;
        # P02 has V001 with 2 anchors + V002 with 1 anchor = 3 rows.
        # Total: 2 + 3 = 5 rows.
        config_path = _write_temp_config(tmp_path)
        df_detail, _ = run_pipeline(config_path)
        assert len(df_detail) == 5

    def test_agg_row_count(self, tmp_path):
        config_path = _write_temp_config(tmp_path)
        _, df_agg = run_pipeline(config_path)
        assert len(df_agg) == 2  # 2 anatomical points

    def test_all_series_positive(self, tmp_path):
        # All 4 mock (visit, point) pairs exceed threshold_pct=300
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

    def test_p02_has_multi_anchor_rows(self, tmp_path):
        # V001/P02 produces 2 anchor rows (M2 and M3 both >= 300)
        config_path = _write_temp_config(tmp_path)
        df_detail, _ = run_pipeline(config_path)
        p02_v001 = df_detail[
            (df_detail["visit_id"] == "V001") &
            (df_detail["point"] == "LH - 1 - a - P02")
        ]
        assert len(p02_v001) == 2
        assert set(p02_v001["anchor_rank"].tolist()) == {1, 2}


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

    def test_detail_csv_row_count(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        df = pd.read_csv(tmp_path / "output" / "cpm_ia_detail.csv")
        assert len(df) == 5  # 5 anchor-level rows

    def test_agg_csv_row_count(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        df = pd.read_csv(tmp_path / "output" / "cpm_ia_aggregated.csv")
        assert len(df) == 2

    def test_detail_csv_has_anchor_columns(self, tmp_path):
        import pandas as pd
        config_path = _write_temp_config(tmp_path)
        run_pipeline(config_path)
        df = pd.read_csv(tmp_path / "output" / "cpm_ia_detail.csv")
        for col in ("anchor_rank", "anchor_marker", "anchor_value", "anchor_index", "positives_count"):
            assert col in df.columns, f"Missing column: {col}"


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



# ---------------------------------------------------------------------------
# Helper for Excel-based integration tests
# ---------------------------------------------------------------------------

def _write_xlsx(path, markers_data):
    """Write wide-format xlsx: first col = marker name, remaining cols = point values."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    points = list({p for vals in markers_data.values() for p in vals})
    ws.append(["Marker / Point"] + points)
    for marker, vals in markers_data.items():
        ws.append([marker] + [vals.get(p) for p in points])
    wb.save(str(path))


def _excel_xml(output_dir, files_data, threshold=300.0):
    """Return XML config string for Excel multi-file input."""
    file_blocks = []
    for visit_id, visit_date, xlsx_path in files_data:
        file_blocks.append(
            "    <file>"
            "<path>" + xlsx_path.as_posix() + "</path>"
            "<visit_id>" + visit_id + "</visit_id>"
            "<visit_date>" + visit_date + "</visit_date>"
            "</file>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<cpm_ia_config>\n'
        '  <input><type>excel</type><csv><path></path></csv><excel>\n'
        + "\n".join(file_blocks) + "\n"
        '  </excel><db><dsn_env>DSN</dsn_env><query></query></db></input>\n'
        '  <output_path>' + output_dir.as_posix() + '</output_path>\n'
        '  <output_label_detail>cpm_ia_detail</output_label_detail>\n'
        '  <output_label_aggregated>cpm_ia_aggregated</output_label_aggregated>\n'
        '  <threshold_pct>' + str(threshold) + '</threshold_pct>\n'
        '  <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>\n'
        '  <n_max>1000</n_max>\n'
        '  <data_quality><drop_invalid_points>true</drop_invalid_points></data_quality>\n'
        '</cpm_ia_config>'
    )


# ---------------------------------------------------------------------------
# TC-11-006 — Per-file Excel output: one subfolder per visit
# ---------------------------------------------------------------------------

class TestTC11006:
    """TC-11-006: Multi-file Excel input produces one output subfolder per visit."""

    def test_per_visit_subfolders_created(self, tmp_path):
        """Each visit gets its own <output_path>/<visit_id>/ subfolder."""
        output_dir = tmp_path / "output"
        xlsx1 = tmp_path / "V001.xlsx"
        xlsx2 = tmp_path / "V002.xlsx"
        _write_xlsx(xlsx1, {"M1": {"LH - 3 - c": 100.0, "LH - 4 - c": 350.0}})
        _write_xlsx(xlsx2, {"M1": {"LH - 3 - c": 200.0, "LH - 4 - c": 400.0}})
        config_path = tmp_path / "config.xml"
        config_path.write_text(_excel_xml(output_dir, [
            ("V001", "2026-01-01", xlsx1),
            ("V002", "2026-02-01", xlsx2),
        ]), encoding="utf-8")
        run_pipeline(config_path)
        assert (output_dir / "V001" / "cpm_ia_detail.csv").exists()
        assert (output_dir / "V002" / "cpm_ia_detail.csv").exists()

    def test_per_visit_outputs_contain_only_own_rows(self, tmp_path):
        """Each subfolder CSV contains only its own visit_id."""
        import pandas as pd
        output_dir = tmp_path / "output"
        xlsx1 = tmp_path / "V001.xlsx"
        xlsx2 = tmp_path / "V002.xlsx"
        _write_xlsx(xlsx1, {"M1": {"LH - 3 - c": 350.0}})
        _write_xlsx(xlsx2, {"M1": {"LH - 3 - c": 400.0}})
        config_path = tmp_path / "config.xml"
        config_path.write_text(_excel_xml(output_dir, [
            ("V001", "2026-01-01", xlsx1),
            ("V002", "2026-02-01", xlsx2),
        ]), encoding="utf-8")
        run_pipeline(config_path)
        df1 = pd.read_csv(output_dir / "V001" / "cpm_ia_detail.csv")
        df2 = pd.read_csv(output_dir / "V002" / "cpm_ia_detail.csv")
        assert set(df1["visit_id"].unique()) == {"V001"}
        assert set(df2["visit_id"].unique()) == {"V002"}


# ---------------------------------------------------------------------------
# TC-11-007 — Batch resilience: empty visit skipped, valid visit processed
# ---------------------------------------------------------------------------

class TestTC11007:
    """TC-11-007: In multi-file mode, empty xlsx is skipped; valid visit succeeds."""

    def test_empty_visit_skipped_valid_processed(self, tmp_path):
        """Empty xlsx (headers only) causes skip; the other visit is still processed."""
        import openpyxl
        output_dir = tmp_path / "output"
        # Empty xlsx — headers only, no data rows
        empty_xlsx = tmp_path / "V_EMPTY.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Marker / Point", "LH - 3 - c"])
        wb.save(str(empty_xlsx))
        # Valid xlsx with one positive anchor
        valid_xlsx = tmp_path / "V_VALID.xlsx"
        _write_xlsx(valid_xlsx, {"M1": {"LH - 3 - c": 350.0}})
        config_path = tmp_path / "config.xml"
        config_path.write_text(_excel_xml(output_dir, [
            ("V_EMPTY", "2026-01-01", empty_xlsx),
            ("V_VALID", "2026-01-02", valid_xlsx),
        ]), encoding="utf-8")
        run_pipeline(config_path)  # must not raise
        assert (output_dir / "V_VALID" / "cpm_ia_detail.csv").exists()
        assert not (output_dir / "V_EMPTY").exists()
