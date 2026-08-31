# LINKED-TO: [REQ-CPM-IA-P26.0002]
"""
data_ingestion.py — Autonomous Raw-Variation Ingestion for the CPM-IA component.

Reads the consolidated raw-percentage-variation CSV produced by the Raw Variation
Computation component, validates its schema, and returns a clean DataFrame.
All field validation occurs here before any downstream computation (G-03).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config_loader import CpmIaConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name constants — confirmed contract with upstream Raw Variation Computation
# Confirmed by [IR] 2026-08-27 (updated 2026-08-28): visit_id, marker, point, percentage_variation, visit_date
# ---------------------------------------------------------------------------

COL_VISIT = "visit_id"
COL_MARKER = "marker"
COL_POINT = "point"
COL_RAW_VARIATION = "percentage_variation"
COL_VISIT_DATE = "visit_date"  # kept as string/object; no datetime parsing at ingestion

REQUIRED_COLUMNS: frozenset[str] = frozenset({
    COL_VISIT,
    COL_MARKER,
    COL_POINT,
    COL_RAW_VARIATION,
    COL_VISIT_DATE,
})

_KEY_ID_COLUMNS: tuple[str, ...] = (COL_VISIT, COL_MARKER, COL_POINT)


class IngestionError(Exception):
    """Raised when the input CSV is missing, malformed, or fails schema validation."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_data(config: CpmIaConfig) -> pd.DataFrame:
    """
    Read and validate the raw-variation CSV at config.input_path.

    Returns a validated long-format DataFrame with COL_RAW_VARIATION as float64
    and COL_VISIT_DATE as string/object. Raises IngestionError on any failure.
    """
    path = Path(config.input_path)

    # Step 1 — file existence and format check
    if not path.exists():
        raise IngestionError(f"Input file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise IngestionError(
            f"Unsupported input format: {path.suffix!r}; expected .csv"
        )

    # Step 2 — read raw (no dtype pre-casting; validation comes next)
    df = pd.read_csv(path, encoding="utf-8")

    # Step 3 — required column presence (G-03)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise IngestionError(f"Missing required column(s): {sorted(missing)}")

    # Step 4 — numeric cast of COL_RAW_VARIATION
    # Genuine NaN (empty cell — missing measurement) is allowed and passes through.
    # Only rows where the original value is non-NaN but numeric coercion fails
    # (e.g. text strings like "high" or "INVALID") are rejected as malformed.
    coerced = pd.to_numeric(df[COL_RAW_VARIATION], errors="coerce")
    invalid_mask = coerced.isna() & df[COL_RAW_VARIATION].notna()
    if invalid_mask.any():
        bad_indices = df.index[invalid_mask].tolist()
        raise IngestionError(
            f"Non-numeric values in {COL_RAW_VARIATION!r} at rows: {bad_indices}"
        )
    df[COL_RAW_VARIATION] = coerced.astype("float64")

    # Step 5 — NaN check in key identifier columns
    bad_mask = df[list(_KEY_ID_COLUMNS)].isna().any(axis=1)
    if bad_mask.any():
        raise IngestionError(
            f"NaN in key columns at rows: {df.index[bad_mask].tolist()}"
        )

    logger.info(
        "CPM-IA input loaded | rows=%d | columns=%s | visits=%d | markers=%d | points=%d",
        len(df),
        sorted(df.columns.tolist()),
        df[COL_VISIT].nunique(),
        df[COL_MARKER].nunique(),
        df[COL_POINT].nunique(),
    )

    return df
