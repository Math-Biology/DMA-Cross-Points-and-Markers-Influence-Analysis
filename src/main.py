# LINKED-TO: [REQ-CPM-IA-P26.0001, REQ-CPM-IA-P26.0002, REQ-CPM-IA-P26.0003,
#              REQ-CPM-IA-P26.0004, REQ-CPM-IA-P26.0005, REQ-CPM-IA-P26.0006,
#              REQ-CPM-IA-P26.0007, REQ-CPM-IA-P26.0008, REQ-CPM-IA-P26.0009,
#              REQ-CPM-IA-P26.0010, REQ-CPM-IA-P26.0011]
"""
main.py — CPM-IA Pipeline Orchestrator.

CLI entry point. Calls Modules 01–11 in the documented execution order,
threading each module's output into the next stage's inputs. Contains no
analytical logic — all computation is delegated to the individual modules.

Usage:
    python -m src.main <config_path>
"""

from __future__ import annotations

import logging
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pandas as pd

from src.config_loader import (
    CpmIaConfig,
    ExcelFileConfig,
    ExcelInputConfig,
    InputConfig,
    load_config,
)
from src.data_ingestion import load_data
from src.descent_descriptors import compute_descriptors
from src.descent_slope import compute_slopes
from src.descent_window import determine_descent_windows
from src.marker_sequence import build_sequences
from src.output_consolidation import consolidate_outputs
from src.positive_census import compute_census
from src.report_generator import generate_report
from src.trigger_detection import detect_triggers
from src.variance_indicator import compute_variance_indicators

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Initialise root logging handler for the CPM-IA pipeline run."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _make_per_file_config(config: CpmIaConfig, file_cfg: ExcelFileConfig) -> CpmIaConfig:
    """Return a config restricted to one Excel file with a visit-specific output subfolder."""
    single_input = InputConfig(
        type="excel",
        csv=config.input.csv,
        excel=ExcelInputConfig(files=(file_cfg,)),
        db=config.input.db,
    )
    return replace(config, input=single_input, output_path=config.output_path / file_cfg.visit_id)


def _run_from_config(config: CpmIaConfig, run_dt: datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Execute M02–M11 from a pre-built config and return (df_detail, df_agg)."""
    logger.info(
        "CPM-IA run | input=%s | output=%s",
        config.input_description(),
        config.output_path,
    )

    df_raw, dq_report = load_data(config)                                        # M02
    marker_orders, sequences = build_sequences(df_raw)                           # M03
    trigger_results = detect_triggers(                                            # M04
        sequences, marker_orders, config.threshold_pct
    )
    census = compute_census(trigger_results)                                      # M05
    descent_windows = determine_descent_windows(                                  # M06
        sequences, trigger_results,
        config.rise_tolerance_epsilon, config.n_max,
    )
    slopes = compute_slopes(descent_windows)                                      # M07
    descriptors = compute_descriptors(descent_windows, trigger_results)           # M08
    variance_indicators = compute_variance_indicators(                            # M09
        sequences, trigger_results, descent_windows
    )
    df_detail, df_agg = consolidate_outputs(                                      # M10
        df_raw, trigger_results, census, descent_windows,
        slopes, descriptors, variance_indicators, config,
    )
    generate_report(                                                               # M11
        df_detail, df_agg, trigger_results, census,
        descent_windows, marker_orders, config, run_dt,
        dq_report,
    )

    logger.info(
        "CPM-IA run complete | detail_rows=%d | agg_rows=%d",
        len(df_detail),
        len(df_agg),
    )
    return df_detail, df_agg


def run_pipeline(config_path: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Execute the full CPM-IA pipeline end-to-end.

    When the input type is 'excel' and multiple files are configured, the pipeline
    runs once per input file, each writing to its own output subfolder
    (<output_path>/<visit_id>/). In batch mode, per-visit errors are caught,
    logged as WARNING, and the remaining visits continue. The last successful
    run's DataFrames are returned.

    Args:
        config_path: Path to the XML configuration file.

    Returns:
        Tuple (df_detail, df_agg) — the tidy DataFrames also written to CSV.

    Raises:
        Any typed exception from Modules 01–11 propagates unchanged in single-visit mode.
    """
    run_dt = datetime.utcnow()
    logger.info(
        "CPM-IA pipeline starting | config=%s | run_dt=%s",
        config_path,
        run_dt.isoformat(),
    )

    config = load_config(config_path)                                             # M01

    if (
        config.input.type == "excel"
        and config.input.excel is not None
        and len(config.input.excel.files) > 1
    ):
        result: Tuple[pd.DataFrame, pd.DataFrame] = (pd.DataFrame(), pd.DataFrame())
        skipped = 0
        total = len(config.input.excel.files)
        for i, file_cfg in enumerate(config.input.excel.files, 1):
            per_config = _make_per_file_config(config, file_cfg)
            try:
                result = _run_from_config(per_config, run_dt)
            except Exception as exc:
                logger.warning(
                    "[%d/%d] Visit %s skipped — %s: %s",
                    i, total, file_cfg.visit_id, type(exc).__name__, exc,
                )
                skipped += 1
        processed = total - skipped
        logger.info(
            "CPM-IA pipeline complete | %d/%d visit(s) processed | %d skipped",
            processed, total, skipped,
        )
        return result

    return _run_from_config(config, run_dt)


def main() -> None:
    """CLI entry point: parse config path from argv, run pipeline, exit 0/1."""
    _configure_logging()

    if len(sys.argv) < 2:
        logging.critical("No config path provided. Usage: python -m src.main <config_path>")
        sys.exit(1)

    try:
        run_pipeline(sys.argv[1])
    except Exception as exc:
        logging.critical("CPM-IA pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
