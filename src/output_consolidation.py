# LINKED-TO: [REQ-CPM-IA-P26.0010]
"""
output_consolidation.py — Consolidated Tidy Output and Per-Point Aggregation
for the CPM-IA component.

Assembles outputs from Modules 04–09 into two tidy CSV files:
  1. Per-(visit, point, anchor) detail table  — {output_path}/{output_label_detail}.csv
  2. Per-point aggregation table              — {output_path}/{output_label_aggregated}.csv

G-09: outputs are in long (tidy) format, uniquely identified by grouping keys.
      Detail uniqueness key: (visit_id, point, anchor_marker).
G-10: raises OutputError if an output file already exists (no silent overwrite).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    "anchor_rank",
    "anchor_marker",
    "anchor_value",
    "anchor_index",
    "positives_count",
    "no_cross_marker_effect",
    "descent_slope",
    "descent_depth",
    "descent_length",
    "mean_per_step_decrease",
    "window_close_reason",
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

# Additional aggregation columns
_AGG_MEDIAN_EXTRA = [
    "median_positives_count",
]


class OutputError(Exception):
    """Raised on file collision, join failure, or G-09 uniqueness violation."""


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_detail(
    df_raw: pd.DataFrame,
    trigger_results: TriggerResults,
    descent_windows: DescentWindows,
    slopes: Slopes,
    descriptors: Descriptors,
    variance_indicators: VarianceIndicators,
) -> pd.DataFrame:
    """Assemble the per-(visit, point, anchor) detail DataFrame."""

    rows = []
    for (visit, point), result in trigger_results.items():
        if result.no_cross_marker_effect:
            # One row per no-effect (visit, point)
            rows.append({
                COL_VISIT: visit,
                COL_POINT: point,
                "anchor_rank": None,
                "anchor_marker": None,
                "anchor_value": None,
                "anchor_index": None,
                "positives_count": 0,
                "no_cross_marker_effect": True,
                "descent_slope": None,
                "descent_depth": None,
                "descent_length": None,
                "mean_per_step_decrease": None,
                "window_close_reason": None,
                "variance_before": None,
                "variance_after": None,
                "variance_ratio": None,
            })
        else:
            anchors = result.anchors
            slope_list = slopes.get((visit, point), [])
            desc_list = descriptors.get((visit, point), [])
            var_list = variance_indicators.get((visit, point), [])
            win_list = descent_windows.get((visit, point), [])

            for i, anchor in enumerate(anchors):
                sl = slope_list[i] if i < len(slope_list) else None
                desc = desc_list[i] if i < len(desc_list) else None
                var_ind = var_list[i] if i < len(var_list) else None
                win = win_list[i] if i < len(win_list) else None

                rows.append({
                    COL_VISIT: visit,
                    COL_POINT: point,
                    "anchor_rank": i + 1,
                    "anchor_marker": anchor.marker,
                    "anchor_value": anchor.value,
                    "anchor_index": anchor.index,
                    "positives_count": result.positives_count,
                    "no_cross_marker_effect": False,
                    "descent_slope": sl,
                    "descent_depth": desc.descent_depth if desc else None,
                    "descent_length": desc.descent_length if desc else None,
                    "mean_per_step_decrease": desc.mean_per_step_decrease if desc else None,
                    "window_close_reason": win.window_close_reason if win else None,
                    "variance_before": var_ind.variance_before if var_ind else None,
                    "variance_after": var_ind.variance_after if var_ind else None,
                    "variance_ratio": var_ind.variance_ratio if var_ind else None,
                })

    df = pd.DataFrame(rows)

    # Derive visit metadata: all df_raw columns except marker-level ones
    meta_cols = [c for c in df_raw.columns if c not in (COL_MARKER, COL_RAW_VARIATION)]
    visit_meta = df_raw[meta_cols].drop_duplicates()

    df = df.merge(visit_meta, on=[COL_VISIT, COL_POINT], how="left")

    # Check for join failures: any (visit, point) in trigger_results absent from df_raw
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

    # G-09: assert unique (visit_id, point, anchor_marker) identification
    if df.duplicated(subset=[COL_VISIT, COL_POINT, "anchor_marker"]).any():
        raise OutputError(
            "Duplicate (visit_id, point, anchor_marker) rows — G-09 uniqueness violated"
        )

    # Apply canonical output column name; order columns per spec
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

    # total_visit_count: unique visit_id per point (count distinct visits, not rows)
    total_counts = (
        df_detail.groupby(OUT_COL_POINT)[COL_VISIT]
        .nunique()
        .rename("total_visit_count")
    )

    # Positive visits: rows where no_cross_marker_effect=False
    df_pos = df_detail[~df_detail["no_cross_marker_effect"]]

    # Positive visit count: unique visits per point in positive rows
    pos_counts = (
        df_pos.groupby(OUT_COL_POINT)[COL_VISIT]
        .nunique()
        .rename("positive_visit_count")
    )

    # median_positives_count: median of positives_count per (visit, point) pair (one value per pair)
    pc_per_pair = (
        df_pos.groupby([OUT_COL_POINT, COL_VISIT])["positives_count"]
        .first()
        .reset_index()
        .groupby(OUT_COL_POINT)["positives_count"]
        .median()
        .rename("median_positives_count")
    )

    # Medians over ALL anchors of the point (all positive rows in detail)
    pos_medians = df_pos.groupby(OUT_COL_POINT)[_MEDIAN_COLS].median(numeric_only=True)
    pos_medians.columns = [f"median_{c}" for c in pos_medians.columns]

    df_agg = (
        total_counts
        .to_frame()
        .join(pos_counts, how="left")
        .join(pc_per_pair, how="left")
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
        df_raw, trigger_results, descent_windows, slopes, descriptors, variance_indicators
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
