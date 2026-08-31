# LINKED-TO: [REQ-CPM-IA-P26.0002]
"""Unit tests for src/data_ingestion.py — TC-02-001 through TC-02-007."""

from pathlib import Path

import pandas as pd
import pytest

from src.config_loader import CpmIaConfig
from src.data_ingestion import (
    COL_MARKER,
    COL_POINT,
    COL_RAW_VARIATION,
    COL_VISIT,
    COL_VISIT_DATE,
    IngestionError,
    REQUIRED_COLUMNS,
    load_data,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _config(input_path: Path) -> CpmIaConfig:
    return CpmIaConfig(
        input_path=input_path,
        output_path=Path("/tmp/output"),
        output_label_detail="detail",
        output_label_aggregated="aggregated",
        threshold_pct=300.0,
        rise_tolerance_epsilon=5.0,
        n_max=10,
    )


_VALID_CSV = (
    "visit_id,marker,point,percentage_variation,visit_date\n"
    "V001,M1,P01,150.0,2026-01-15\n"
    "V001,M2,P01,320.5,2026-01-15\n"
    "V001,M1,P02,80.0,2026-01-15\n"
    "V002,M1,P01,200.0,2026-02-20\n"
    "V002,M2,P01,410.0,2026-02-20\n"
)


def _write(tmp_path: Path, content: str, name: str = "data.csv") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# TC-02-001 — Valid CSV
# ---------------------------------------------------------------------------

def test_tc_02_001_valid_csv_returns_dataframe(tmp_path: Path) -> None:
    """Valid CSV: returns DataFrame with correct shape and dtypes."""
    df = load_data(_config(_write(tmp_path, _VALID_CSV)))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert df[COL_RAW_VARIATION].dtype == "float64"
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))


def test_tc_02_001_visit_date_kept_as_string(tmp_path: Path) -> None:
    """visit_date must remain object/string dtype — no datetime parsing at ingestion."""
    df = load_data(_config(_write(tmp_path, _VALID_CSV)))
    assert df[COL_VISIT_DATE].dtype == object


def test_tc_02_001_unique_counts(tmp_path: Path) -> None:
    """Valid CSV: correct unique visit/marker/point counts."""
    df = load_data(_config(_write(tmp_path, _VALID_CSV)))
    assert df[COL_VISIT].nunique() == 2
    assert df[COL_MARKER].nunique() == 2
    assert df[COL_POINT].nunique() == 2


# ---------------------------------------------------------------------------
# TC-02-002 — Missing required column
# ---------------------------------------------------------------------------

def test_tc_02_002_missing_marker_column(tmp_path: Path) -> None:
    """CSV missing marker raises IngestionError naming the column."""
    csv = (
        "visit_id,point_id,raw_pct_variation,visit_date\n"
        "V001,P01,150.0,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="marker"):
        load_data(_config(_write(tmp_path, csv)))


def test_tc_02_002_missing_multiple_columns(tmp_path: Path) -> None:
    """CSV missing several required columns raises IngestionError listing all."""
    csv = "visit_id,point_id\nV001,P01\n"
    with pytest.raises(IngestionError, match="Missing required column"):
        load_data(_config(_write(tmp_path, csv)))


# ---------------------------------------------------------------------------
# TC-02-003 — Non-numeric percentage_variation
# ---------------------------------------------------------------------------

def test_tc_02_003_raw_variation_na_string_passes(tmp_path: Path) -> None:
    """percentage_variation = 'N/A' is auto-converted to NaN by pandas — treated as
    a genuine missing measurement and allowed through without error."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,P01,150.0,2026-01-15\n"
        "V001,M2,P01,N/A,2026-01-15\n"
    )
    df = load_data(_config(_write(tmp_path, csv)))
    assert len(df) == 2
    import math
    assert math.isnan(df.iloc[1]["percentage_variation"])


def test_tc_02_003_raw_variation_text(tmp_path: Path) -> None:
    """percentage_variation = arbitrary non-numeric text raises IngestionError."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,P01,high,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="percentage_variation"):
        load_data(_config(_write(tmp_path, csv)))


def test_tc_02_003_raw_variation_empty_cell_passes(tmp_path: Path) -> None:
    """percentage_variation empty cell is NaN — treated as a genuine missing
    measurement and allowed through without error."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,P01,,2026-01-15\n"
    )
    df = load_data(_config(_write(tmp_path, csv)))
    assert len(df) == 1
    import math
    assert math.isnan(df.iloc[0]["percentage_variation"])


def test_tc_02_003_nan_missing_measurement_passes(tmp_path: Path) -> None:
    """Mixed rows: some with valid values, some genuinely missing — all pass through."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,P01,150.0,2026-01-15\n"
        "V001,M2,P01,,2026-01-15\n"
        "V002,M1,P01,200.0,2026-02-20\n"
    )
    df = load_data(_config(_write(tmp_path, csv)))
    assert len(df) == 3
    assert df["percentage_variation"].dtype == "float64"


# ---------------------------------------------------------------------------
# TC-02-004 — NaN in key identifier columns
# ---------------------------------------------------------------------------

def test_tc_02_004_nan_in_visit_id(tmp_path: Path) -> None:
    """Empty visit_id cell raises IngestionError with row indices."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,P01,150.0,2026-01-15\n"
        ",M2,P01,320.5,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="NaN in key columns"):
        load_data(_config(_write(tmp_path, csv)))


def test_tc_02_004_nan_in_point(tmp_path: Path) -> None:
    """Empty point cell raises IngestionError."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,M1,,150.0,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="NaN in key columns"):
        load_data(_config(_write(tmp_path, csv)))


def test_tc_02_004_nan_in_marker(tmp_path: Path) -> None:
    """Empty marker cell raises IngestionError."""
    csv = (
        "visit_id,marker,point,percentage_variation,visit_date\n"
        "V001,,P01,150.0,2026-01-15\n"
    )
    with pytest.raises(IngestionError, match="NaN in key columns"):
        load_data(_config(_write(tmp_path, csv)))


# ---------------------------------------------------------------------------
# TC-02-005 — File not found
# ---------------------------------------------------------------------------

def test_tc_02_005_file_not_found(tmp_path: Path) -> None:
    """Non-existent path raises IngestionError mentioning 'not found'."""
    with pytest.raises(IngestionError, match="not found"):
        load_data(_config(tmp_path / "missing.csv"))


# ---------------------------------------------------------------------------
# TC-02-006 — Unsupported file format
# ---------------------------------------------------------------------------

def test_tc_02_006_xlsx_extension_rejected(tmp_path: Path) -> None:
    """File with .xlsx extension raises IngestionError."""
    p = tmp_path / "data.xlsx"
    p.write_text("fake", encoding="utf-8")
    with pytest.raises(IngestionError, match="Unsupported input format"):
        load_data(_config(p))


def test_tc_02_006_txt_extension_rejected(tmp_path: Path) -> None:
    """File with .txt extension raises IngestionError even if content is valid CSV."""
    p = tmp_path / "data.txt"
    p.write_text(_VALID_CSV, encoding="utf-8")
    with pytest.raises(IngestionError, match="Unsupported input format"):
        load_data(_config(p))


# ---------------------------------------------------------------------------
# TC-02-007 — Empty CSV (header only, zero data rows)
# ---------------------------------------------------------------------------

def test_tc_02_007_header_only_returns_empty_dataframe(tmp_path: Path) -> None:
    """CSV with headers but zero rows returns an empty DataFrame without error."""
    csv = "visit_id,marker,point,percentage_variation,visit_date\n"
    df = load_data(_config(_write(tmp_path, csv)))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))
