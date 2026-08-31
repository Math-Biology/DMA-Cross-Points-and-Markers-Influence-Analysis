# LINKED-TO: [REQ-CPM-IA-P26.0010]
"""
output_consolidation.py — Consolidated Tidy Output and Per-Point Aggregation
for the CPM-IA component.

Assembles outputs from Modules 04–09 into two tidy CSV files:
  1. Per-(visit, point) detail table    — {output_path}/{output_label_detail}.csv
  2. Per-point aggregation table        — {output_path}/{output_label_aggregated}.csv

G-09: outputs are in long (tidy) format, uniquely identified by grouping keys.
G-10: raises OutputError if an output file already exists (no silent overwrite).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from src.config_loader import CpmIaConfig
from src.data_ingestion import COL_MARKER, COL_POINT, COL_RAW_VARIATION, COL_VISIT
from src.descent_descriptors import Descriptors
from src.descent_slope import Slopes
from src.descent_window import DescentWindows
from src.positive_census import PointCensus
from src.trigger_detection import TriggerResults
from src.variance_indicator import VarianceIndicators

logger = logging.getLogger(__name__)

# Output column name for anatomical point (equals COL_POINT = "point")
OUT_COL_POINT = "point"

# Fixed ordering of analytical columns in detail output
_ANALYTICAL_COLS = [
    "first_positive_marker",
    "first_positive_value",
    "no_cross_marker_effect",
    "descent_slope",
    "descent_depth",
    "descent_length",
    "mean_per_step_decrease",
    "variance_before",
    "variance_after",
    "variance_ratio",
]

# Analytical columns whose medians appear in the aggregation table
_MEDIAN_COLS = [
    "descent_slope",
    "descent_depth",
    "descent_length",
    "mean_per_step_decrease",
]


class OutputError(Exception):
    """Raised on file collision, join failure, or G-09 uniqueness violation."""


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_detail(
    df_raw: pd.DataFrame,
    trigger_results: TriggerResults,
    slopes: Slopes,
    descriptors: Descriptors,
    variance_indicators: VarianceIndicators,
) -> pd.DataFrame:
    """Assemble the per-(visit, point) detail DataFrame."""

    # --- 1. Build flat rows from all computed module outputs ---
    rows = []
    for (visit, point), result in trigger_results.items():
        desc = descriptors.get((visit, point))
        var_ind = variance_indicators.get((visit, point))

        rows.append({
            COL_VISIT: visit,
            COL_POINT: point,
            "first_positive_marker": result.first_positive_marker,
            "first_positive_value": result.first_positive_value,
            "no_cross_marker_effect": result.no_cross_marker_effect,
            "descent_slope": slopes.get((visit, point)),
            "descent_depth": desc.descent_depth if desc is not None else None,
            "descent_length": desc.descent_length if desc is not None else None,
            "mean_per_step_decrease": desc.mean_per_step_decrease if desc is not None else None,
            "variance_before": var_ind.variance_before if var_ind is not None else None,
            "variance_after": var_ind.variance_after if var_ind is not None else None,
            "variance_ratio": var_ind.variance_ratio if var_ind is not None else None,
        })

    df = pd.DataFrame(rows)

    # --- 2. Derive visit metadata: all df_raw columns except marker-level ones ---
    meta_cols = [c for c in df_raw.columns if c not in (COL_MARKER, COL_RAW_VARIATION)]
    visit_meta = df_raw[meta_cols].drop_duplicates()

    df = df.merge(visit_meta, on=[COL_VISIT, COL_POINT], how="left")

    # --- 3. Check for join failures: any (visit, point) in trigger_results absent from df_raw ---
    # NaN in non-key metadata columns is allowed (source data may have missing visit_date etc.).
    # A true join failure is detected by checking whether the trigger_results keys are all
    # represented in visit_meta — an absent key produces all-NaN non-key columns for that row.
    visit_meta_keys = set(
        zip(visit_meta[COL_VISIT].astype(str), visit_meta[COL_POINT].astype(str))
    )
    missing_keys = [
        (v, p)
        for v, p in zip(df[COL_VISIT].astype(str), df[COL_POINT].astype(str))
        if (v, p) not in visit_meta_keys
    ]
    if missing_keys:
        raise OutputError(
            f"Join failure: {len(missing_keys)} (visit, point) pair(s) from trigger_results "
            f"have no metadata row in df_raw — first missing: {missing_keys[0]}"
        )

    # --- 4. G-09: assert unique (visit, point) identification after join ---
    if df.duplicated(subset=[COL_VISIT, COL_POINT]).any():
        raise OutputError(
            "Duplicate (visit, point) rows after metadata join — G-09 uniqueness violated"
        )

    # --- 5. Apply canonical output column name; order columns per spec ---
    df = df.rename(columns={COL_POINT: OUT_COL_POINT})
    visit_meta_output_cols = [
        c if c != COL_POINT else OUT_COL_POINT
        for c in meta_cols
        if c != COL_POINT
    ]
    df = df[visit_meta_output_cols + [OUT_COL_POINT] + _ANALYTICAL_COLS]

    return df


def _build_aggregation(df_detail: pd.DataFrame) -> pd.DataFrame:
    """Build the per-point aggregation DataFrame from the detail DataFrame."""

    # Total visits per point (all rows)
    total_counts = df_detail.groupby(OUT_COL_POINT).size().rename("total_visit_count")

    # Positive visits subset
    df_pos = df_detail[~df_detail["no_cross_marker_effect"]]

    # Positive visit count per point
    pos_counts = (
        df_pos.groupby(OUT_COL_POINT).size().rename("positive_visit_count")
    )

    # Medians over positive visits only (pandas .median() skips NaN by default)
    pos_medians = df_pos.groupby(OUT_COL_POINT)[_MEDIAN_COLS].median()
    pos_medians.columns = [f"median_{c}" for c in pos_medians.columns]

    df_agg = (
        total_counts
        .to_frame()
        .join(pos_counts, how="left")
        .join(pos_medians, how="left")
        .reset_index()
    )

    df_agg["positive_visit_count"] = (
        df_agg["positive_visit_count"].fillna(0).astype(int)
    )
    df_agg["positive_prevalence"] = (
        df_agg["positive_visit_count"] / df_agg["total_visit_count"]
    )

    return df_agg


def _cross_check_census(census: PointCensus, df_agg: pd.DataFrame) -> None:
    """Warn if census counts diverge from aggregation counts (internal consistency)."""
    actual_total = len(df_agg)
    actual_positive = int((df_agg["positive_visit_count"] > 0).sum())

    if actual_total != census.total_point_count:
        logger.warning(
            "Census cross-check: total_point_count mismatch "
            "(census=%d, aggregation=%d)",
            census.total_point_count,
            actual_total,
        )
    if actual_positive != census.positive_point_count:
        logger.warning(
            "Census cross-check: positive_point_count mismatch "
            "(census=%d, aggregation=%d)",
            census.positive_point_count,
            actual_positive,
        )


def _write_outputs(
    df_detail: pd.DataFrame,
    df_agg: pd.DataFrame,
    config: CpmIaConfig,
) -> Tuple[Path, Path]:
    """Write both DataFrames to CSV; raise OutputError on file collision."""
    output_path = Path(config.output_path)

    if not output_path.exists():
        logger.warning("Output directory does not exist; creating: %s", output_path)
        output_path.mkdir(parents=True, exist_ok=True)

    detail_path = output_path / f"{config.output_label_detail}.csv"
    agg_path = output_path / f"{config.output_label_aggregated}.csv"

    if detail_path.exists():
        raise OutputError(f"Output file already exists: {detail_path}")
    if agg_path.exists():
        raise OutputError(f"Output file already exists: {agg_path}")

    df_detail.to_csv(detail_path, index=False, encoding="utf-8")
    df_agg.to_csv(agg_path, index=False, encoding="utf-8")

    logger.info(
        "CPM-IA detail output written | path=%s | rows=%d",
        detail_path,
        len(df_detail),
    )
    logger.info(
        "CPM-IA aggregation output written | path=%s | rows=%d",
        agg_path,
        len(df_agg),
    )

    return detail_path, agg_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def consolidate_outputs(
    df_raw: pd.DataFrame,
    trigger_results: TriggerResults,
    census: PointCensus,
    descent_windows: DescentWindows,
    slopes: Slopes,
    descriptors: Descriptors,
    variance_indicators: VarianceIndicators,
    config: CpmIaConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Assemble all CPM-IA results into two tidy CSV outputs.

    Args:
        df_raw:              Original validated DataFrame from Module 02.
        trigger_results:     Anchor detection results from Module 04.
        census:              Positive-point census from Module 05 (cross-validation only).
        descent_windows:     Descent windows from Module 06.
        slopes:              OLS slopes from Module 07.
        descriptors:         Shape descriptors from Module 08.
        variance_indicators: Pre/post variance from Module 09.
        config:              CpmIaConfig with output paths and label suffixes.

    Returns:
        Tuple (df_detail, df_agg) — both DataFrames also written to CSV.

    Raises:
        OutputError: if a target CSV already exists, if the metadata join fails,
        or if G-09 uniqueness is violated.
    """
    df_detail = _build_detail(
        df_raw, trigger_results, slopes, descriptors, variance_indicators
    )
    df_agg = _build_aggregation(df_detail)
    _cross_check_census(census, df_agg)
    _write_outputs(df_detail, df_agg, config)

    logger.debug(
        "CPM-IA consolidation complete | detail_rows=%d | agg_rows=%d",
        len(df_detail),
        len(df_agg),
    )

    return df_detail, df_agg
