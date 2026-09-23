# LINKED-TO: [REQ-CPM-IA-P26.0002]
"""Unit tests for src/data_ingestion.py — TC-02-001 through TC-02-015."""

from pathlib import Path

import pandas as pd
import pytest

from src.config_loader import (
    CpmIaConfig, CsvInputConfig, DataQualityConfig,
    ExcelFileConfig, ExcelInputConfig, InputConfig,
)
from src.data_ingestion import (
    COL_MARKER, COL_POINT, COL_RAW_VARIATION, COL_VISIT, COL_VISIT_DATE,
    CsvSource, ExcelSource, PostgresSource,
    DataQualityReport, IngestionError, REQUIRED_COLUMNS, load_data,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_csv_config(input_path: Path) -> CpmIaConfig:
    return CpmIaConfig(
        input=InputConfig(
            type="csv",
            csv=CsvInputConfig(path=input_path),
            excel=None,
            db=None,
        ),
        output_path=Path("/tmp/output"),
        output_label_detail="detail",
        output_label_aggregated="aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=True),
    )


def _make_excel_config(files) -> CpmIaConfig:
    return CpmIaConfig(
        input=InputConfig(
            type="excel",
            csv=None,
            excel=ExcelInputConfig(files=tuple(files)),
            db=None,
        ),
        output_path=Path("/tmp/output"),
        output_label_detail="detail",
        output_label_aggregated="aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=True),
    )


_VALID_CSV = (
    "visit_id,marker,point,percentage_variation,visit_date\n"
    "V001,M1,LH - 2 - i - colon,150.0,2026-01-15\n"
    "V001,M2,LH - 2 - i - colon,320.5,2026-01-15\n"
    "V001,M1,LH - 3 - e - Liver,80.0,2026-01-15\n"
    "V002,M1,LH - 2 - i - colon,200.0,2026-02-20\n"
    "V002,M2,LH - 2 - i - colon,410.0,2026-02-20\n"
)


def _write(tmp_path: Path, content: str, name: str = "data.csv") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# TC-02-001 — Valid CSV via load_data returns (DataFrame, DataQualityReport)
# ---------------------------------------------------------------------------

def test_tc_02_001_valid_csv_returns_tuple(tmp_path):
    result = load_data(_make_csv_config(_write(tmp_path, _VALID_CSV)))
    assert isinstance(result, tuple) and len(result) == 2


def test_tc_02_001_valid_csv_dataframe_shape(tmp_path):
    df, _ = load_data(_make_csv_config(_write(tmp_path, _VALID_CSV)))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert df[COL_RAW_VARIATION].dtype == "float64"
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))


def test_tc_02_001_visit_date_kept_as_string(tmp_path):
    df, _ = load_data(_make_csv_config(_write(tmp_path, _VALID_CSV)))
    assert df[COL_VISIT_DATE].dtype == object


def test_tc_02_001_dq_report_fields(tmp_path):
    _, dq = load_data(_make_csv_config(_write(tmp_path, _VALID_CSV)))
    assert isinstance(dq, DataQualityReport)
    assert dq.total_rows == 5
    assert dq.rows_dropped_empty_keys == 0


# ---------------------------------------------------------------------------
# TC-02-002 — Missing required column
# ---------------------------------------------------------------------------

def test_tc_02_002_missing_marker_column(tmp_path):
    csv = (
        "visit_id,point_id,raw_pct_variation,visit_date\n"
        "V001,LH - 2 - i - colon,150.0,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="marker"):
        load_data(_make_csv_config(_write(tmp_path, csv)))


# ---------------------------------------------------------------------------
# TC-02-003 — Non-numeric percentage_variation
# ---------------------------------------------------------------------------

def test_tc_02_003_raw_variation_na_string_passes(tmp_path):
    import math
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 2 - i - colon,150.0,2026-01-15\n"
        "V001,M2,LH - 2 - i - colon,N/A,2026-01-15\n"
    )
    df, _ = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert len(df) == 2
    assert math.isnan(df.iloc[1]["percentage_variation"])


def test_tc_02_003_raw_variation_text_raises(tmp_path):
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 2 - i - colon,high,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="percentage_variation"):
        load_data(_make_csv_config(_write(tmp_path, csv)))


# ---------------------------------------------------------------------------
# TC-02-004 — NaN in key identifier columns
# ---------------------------------------------------------------------------

def test_tc_02_004_nan_in_visit_id(tmp_path):
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 2 - i - colon,150.0,2026-01-15\n"
        ",M2,LH - 2 - i - colon,320.5,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="NaN in key columns"):
        load_data(_make_csv_config(_write(tmp_path, csv)))


# ---------------------------------------------------------------------------
# TC-02-005 — File not found
# ---------------------------------------------------------------------------

def test_tc_02_005_file_not_found(tmp_path):
    with pytest.raises(IngestionError, match="not found"):
        load_data(_make_csv_config(tmp_path / "missing.csv"))


# ---------------------------------------------------------------------------
# TC-02-006 — Unsupported file format (CSV source only)
# ---------------------------------------------------------------------------

def test_tc_02_006_xlsx_extension_rejected(tmp_path):
    p = tmp_path / "data.xlsx"
    p.write_text("fake", encoding="utf-8")
    with pytest.raises(IngestionError, match="Unsupported input format"):
        load_data(_make_csv_config(p))


# ---------------------------------------------------------------------------
# TC-02-007 — Empty CSV (header only, zero data rows)
# ---------------------------------------------------------------------------

def test_tc_02_007_header_only_returns_empty_dataframe(tmp_path):
    csv = "visit_id,marker,point,percentage_variation,visit_date\n"
    df, _ = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))


# ---------------------------------------------------------------------------
# TC-02-008 — Excel source dispatch
# ---------------------------------------------------------------------------

def test_tc_02_008_excel_dispatch_loads_data(tmp_path):
    """ExcelSource melt from a real xlsx file via config dispatch."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Marker / Point", "LH - 2 - i - colon", "RF - 5 - e - Bladder"])
    ws.append(["MarkerA", 150.0, 200.0])
    ws.append(["MarkerB", 350.0, 100.0])
    xlsx_path = tmp_path / "test_visit.xlsx"
    wb.save(str(xlsx_path))

    config = _make_excel_config([
        ExcelFileConfig(path=xlsx_path, visit_id="V001", visit_date="2026-01-01")
    ])
    df, dq = load_data(config)
    assert len(df) == 4  # 2 markers x 2 points
    assert set(df[COL_VISIT].unique()) == {"V001"}
    assert set(df[COL_VISIT_DATE].unique()) == {"2026-01-01"}
    assert "LH - 2 - i - colon" in df[COL_POINT].values
    assert "RF - 5 - e - Bladder" in df[COL_POINT].values


def test_tc_02_008_excel_skips_null_column_headers(tmp_path):
    """Columns with None/empty header are skipped during Excel melt."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Marker / Point", "LH - 2 - i - colon", None, "RF - 5 - e - Bladder"])
    ws.append(["MarkerA", 150.0, 999.0, 200.0])
    xlsx_path = tmp_path / "test_null_col.xlsx"
    wb.save(str(xlsx_path))

    config = _make_excel_config([
        ExcelFileConfig(path=xlsx_path, visit_id="V001", visit_date="2026-01-01")
    ])
    df, _ = load_data(config)
    # Only 2 valid point columns: 1 marker x 2 points = 2 rows
    assert len(df) == 2
    assert None not in df[COL_POINT].values


def test_tc_02_008_excel_multi_file_concat(tmp_path):
    """ExcelSource concatenates rows from multiple files."""
    import openpyxl
    for visit_id, fname in [("V001", "v1.xlsx"), ("V002", "v2.xlsx")]:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Marker / Point", "LH - 2 - i - colon"])
        ws.append(["MarkerA", 100.0])
        wb.save(str(tmp_path / fname))

    config = _make_excel_config([
        ExcelFileConfig(path=tmp_path / "v1.xlsx", visit_id="V001", visit_date="2026-01-01"),
        ExcelFileConfig(path=tmp_path / "v2.xlsx", visit_id="V002", visit_date="2026-02-01"),
    ])
    df, _ = load_data(config)
    assert len(df) == 2
    assert set(df[COL_VISIT].unique()) == {"V001", "V002"}


# ---------------------------------------------------------------------------
# TC-02-009 — PostgresSource raises IngestionError (stub)
# ---------------------------------------------------------------------------

def test_tc_02_009_postgres_stub_raises(tmp_path):
    from src.config_loader import DbInputConfig
    config = CpmIaConfig(
        input=InputConfig(
            type="db",
            csv=None,
            excel=None,
            db=DbInputConfig(dsn_env="MY_DSN", query="SELECT 1"),
        ),
        output_path=Path("/tmp/output"),
        output_label_detail="detail",
        output_label_aggregated="aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=True),
    )
    with pytest.raises(IngestionError, match="Postgres source not configured"):
        load_data(config)


# ---------------------------------------------------------------------------
# TC-02-010 — Invalid point names dropped (drop_invalid_points=True)
# ---------------------------------------------------------------------------

def test_tc_02_010_invalid_point_dropped(tmp_path):
    """Point name 'ciao' is invalid; row is dropped when drop_invalid_points=True."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 2 - i - colon,150.0,2026-01-15\n"
        "V001,M2,ciao,320.5,2026-01-15\n"
    )
    df, dq = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert "ciao" not in df[COL_POINT].values
    assert "ciao" in dq.invalid_point_names
    assert dq.rows_affected_invalid_points == 1
    assert dq.drop_mode is True


def test_tc_02_010_invalid_point_kept_when_drop_false(tmp_path):
    """Point name 'ciao' is kept when drop_invalid_points=False."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 2 - i - colon,150.0,2026-01-15\n"
        "V001,M2,ciao,320.5,2026-01-15\n"
    )
    config = CpmIaConfig(
        input=InputConfig(
            type="csv",
            csv=CsvInputConfig(path=_write(tmp_path, csv)),
            excel=None, db=None,
        ),
        output_path=Path("/tmp/output"),
        output_label_detail="detail",
        output_label_aggregated="aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
        data_quality=DataQualityConfig(drop_invalid_points=False),
    )
    df, dq = load_data(config)
    assert "ciao" in df[COL_POINT].values
    assert dq.drop_mode is False
    assert dq.rows_affected_invalid_points == 1


# ---------------------------------------------------------------------------
# TC-02-011 — Three-component point names (LH - 3 - c) are valid
# ---------------------------------------------------------------------------

def test_tc_02_011_three_component_valid(tmp_path):
    """Point name 'LH - 3 - c' (3 components, no organ label) is accepted."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 3 - c,150.0,2026-01-15\n"
        "V001,M2,LF - 2 - i,320.5,2026-01-15\n"
    )
    df, dq = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert len(df) == 2
    assert len(dq.invalid_point_names) == 0


def test_tc_02_011_two_component_still_invalid(tmp_path):
    """Point name 'LH - 3' (only 2 components) remains invalid."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 3,150.0,2026-01-15\n"
        "V001,M2,LH - 3 - c,320.5,2026-01-15\n"
    )
    df, dq = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert "LH - 3" in dq.invalid_point_names
    assert "LH - 3 - c" not in dq.invalid_point_names


def test_tc_02_011_four_component_still_valid(tmp_path):
    """Four-component point names remain valid alongside three-component ones."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,LH - 5 - e - Small intestine,150.0,2026-01-15\n"
        "V001,M2,RF - 1 - c,320.5,2026-01-15\n"
    )
    df, dq = load_data(_make_csv_config(_write(tmp_path, csv)))
    assert len(df) == 2
    assert len(dq.invalid_point_names) == 0
