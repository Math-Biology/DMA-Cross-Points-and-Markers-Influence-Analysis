# LINKED-TO: [REQ-CPM-IA-P26.0011]
"""
report_generator.py — Automated PDF Run Report for the CPM-IA component (M11).

Fills a LaTeX template with run statistics and compiled analysis results,
then compiles the .tex source to PDF via pdflatex (two passes for correct
table-of-contents page numbers).  If compilation fails, the .tex source is
preserved in the output directory and a ReportError is raised.

Output artefacts written to config.output_path:
    {report_stem}.tex   — filled LaTeX source (always written)
    {report_stem}.pdf   — compiled report (on success)

report_stem is derived from output_label_detail by replacing the ``_detail``
suffix with ``_report`` (e.g. ``cpm_ia_detail`` → ``cpm_ia_report``).
"""

from __future__ import annotations

import logging
import math
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from src.config_loader import CpmIaConfig
from src.descent_window import DescentWindows
from src.marker_sequence import PerVisitMarkerOrders
from src.positive_census import PointCensus
from src.trigger_detection import TriggerResults

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = (
    Path(__file__).parent.parent / "data" / "templates" / "cpm_ia_report.tex.template"
)

# Strip C1 control characters (U+0080–U+009F): double-encoded UTF-8 artefacts
# that pdflatex cannot handle even with utf8 inputenc.
_C1_CTRL_DEL = str.maketrans("", "", "".join(chr(i) for i in range(0x80, 0xA0)))

# LaTeX special-character translation table (text mode only).
_LATEX_TRANS = str.maketrans({
    "\\": r"\textbackslash{}",
    "&":  r"\&",
    "%":  r"\%",
    "$":  r"\$",
    "#":  r"\#",
    "_":  r"\_",
    "{":  r"\{",
    "}":  r"\}",
    "~":  r"\textasciitilde{}",
    "^":  r"\textasciicircum{}",
})


class ReportError(Exception):
    """Raised when report generation or PDF compilation fails."""


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _escape(value: object) -> str:
    """Return a LaTeX-safe string representation of *value*."""
    return str(value).translate(_C1_CTRL_DEL).translate(_LATEX_TRANS)


def _fmt(value: object, decimals: int = 2) -> str:
    """Format *value* as a fixed-point string. Returns ``---`` for None / NaN."""
    if value is None:
        return "---"
    try:
        if pd.isna(value):  # type: ignore[arg-type]
            return "---"
    except (TypeError, ValueError):
        pass
    return f"{float(value):.{decimals}f}"


def _fill_template(template: str, values: Dict[str, str]) -> str:
    """Replace every ``__KEY__`` placeholder in *template* with ``values[KEY]``."""
    for key, val in values.items():
        template = template.replace(f"__{key}__", val)
    return template


def _build_values(
    df_detail: pd.DataFrame,
    df_agg: pd.DataFrame,
    trigger_results: TriggerResults,
    census: PointCensus,
    descent_windows: DescentWindows,
    marker_orders: PerVisitMarkerOrders,
    config: CpmIaConfig,
    run_dt: datetime,
) -> Dict[str, str]:
    """Compute all template placeholder values from pipeline outputs."""
    total_series = len(trigger_results)
    positive_series = sum(
        1 for r in trigger_results.values() if not r.no_cross_marker_effect
    )
    no_effect_series = total_series - positive_series
    positive_rate = positive_series / total_series * 100 if total_series else 0.0
    no_effect_rate = 100.0 - positive_rate

    positive_points = census.positive_point_count
    total_point_count = census.total_point_count
    no_effect_points = total_point_count - positive_points
    positive_points_rate = (
        positive_points / total_point_count * 100 if total_point_count else 0.0
    )
    no_effect_points_rate = 100.0 - positive_points_rate

    truncated = sum(
        1 for w in descent_windows.values()
        if w is not None and w.truncated_by_n_max
    )
    truncated_rate = truncated / positive_series * 100 if positive_series else 0.0

    total_markers = len(
        {m for markers in marker_orders.values() for m in markers}
    )

    # Per-point counts table rows (sorted by point name)
    counts_rows = []
    for _, row in df_agg.sort_values("point").iterrows():
        counts_rows.append(
            f"{_escape(row['point'])} & "
            f"{int(row['total_visit_count'])} & "
            f"{int(row['positive_visit_count'])} & "
            f"{row['positive_prevalence'] * 100:.1f} \\\\"
        )

    # Per-point descent medians table rows (sorted by point name)
    median_rows = []
    for _, row in df_agg.sort_values("point").iterrows():
        median_rows.append(
            f"{_escape(row['point'])} & "
            f"{_fmt(row.get('median_descent_slope'))} & "
            f"{_fmt(row.get('median_descent_depth'))} & "
            f"{_fmt(row.get('median_descent_length'), decimals=1)} & "
            f"{_fmt(row.get('median_mean_per_step_decrease'))} \\\\"
        )

    # Anchor marker summary: per (point, anchor_marker) visit count
    df_pos_detail = df_detail[~df_detail["no_cross_marker_effect"]]
    if not df_pos_detail.empty:
        anchor_summary = (
            df_pos_detail
            .groupby(["point", "first_positive_marker"])
            .size()
            .reset_index(name="anchor_count")
        )
        anchor_summary = anchor_summary.merge(
            df_agg[["point", "positive_visit_count"]], on="point", how="left"
        )
        anchor_summary["anchor_pct"] = (
            anchor_summary["anchor_count"] / anchor_summary["positive_visit_count"] * 100
        )
        anchor_summary = anchor_summary[anchor_summary["anchor_pct"] >= 3.5]
        anchor_summary = anchor_summary.sort_values(
            ["point", "anchor_count"], ascending=[True, False]
        )
        anchor_rows = [
            f"{_escape(row['point'])} & "
            f"{_escape(str(row['first_positive_marker']))} & "
            f"{int(row['anchor_count'])} & "
            f"{row['anchor_pct']:.1f} \\\\"
            for _, row in anchor_summary.iterrows()
        ]
    else:
        anchor_rows = []

    return {
        "RUN_DATE":                   run_dt.strftime("%Y-%m-%d"),
        "RUN_TIME":                   run_dt.strftime("%H:%M:%S"),
        "INPUT_PATH":                 _escape(str(config.input_path)),
        "OUTPUT_PATH":                _escape(str(config.output_path)),
        "OUTPUT_LABEL_DETAIL":        _escape(config.output_label_detail),
        "OUTPUT_LABEL_AGGREGATED":    _escape(config.output_label_aggregated),
        "THRESHOLD_PCT":              f"{config.threshold_pct:.1f}",
        "RISE_EPSILON":               str(config.rise_tolerance_epsilon),
        "N_MAX":                      str(config.n_max),
        "TOTAL_VISITS":               str(df_detail["visit_id"].nunique()),
        "TOTAL_POINTS":               str(total_point_count),
        "TOTAL_MARKERS":              str(total_markers),
        "TOTAL_SERIES":               str(total_series),
        "POSITIVE_SERIES":            str(positive_series),
        "NO_EFFECT_SERIES":           str(no_effect_series),
        "POSITIVE_RATE":              f"{positive_rate:.1f}",
        "NO_EFFECT_RATE":             f"{no_effect_rate:.1f}",
        "POSITIVE_POINTS":            str(positive_points),
        "NO_EFFECT_POINTS":           str(no_effect_points),
        "TOTAL_POINT_COUNT":          str(total_point_count),
        "POSITIVE_POINTS_RATE":       f"{positive_points_rate:.1f}",
        "NO_EFFECT_POINTS_RATE":      f"{no_effect_points_rate:.1f}",
        "TRUNCATED_COUNT":            str(truncated),
        "TRUNCATED_RATE":             f"{truncated_rate:.1f}",
        "AGG_TABLE_COUNTS":           "\n".join(counts_rows),
        "AGG_TABLE_MEDIANS":          "\n".join(median_rows),
        "ANCHOR_TABLE_ROWS":          "\n".join(anchor_rows),
        "ANCHOR_TABLE_THRESHOLD":      "3.5",
    }


def _run_pdflatex(tex_path: Path, output_dir: Path) -> None:
    """Execute one pdflatex pass. Raises ReportError on non-zero exit code."""
    result = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory", str(output_dir),
            str(tex_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        log_tail = "\n".join(result.stdout.splitlines()[-25:])
        raise ReportError(
            f"pdflatex failed (exit {result.returncode}).\n{log_tail}"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_report(
    df_detail: pd.DataFrame,
    df_agg: pd.DataFrame,
    trigger_results: TriggerResults,
    census: PointCensus,
    descent_windows: DescentWindows,
    marker_orders: PerVisitMarkerOrders,
    config: CpmIaConfig,
    run_dt: datetime,
) -> Path:
    """
    Generate the automated PDF run report for the CPM-IA component (M11).

    Args:
        df_detail:        Per-(visit, point) detail DataFrame from Module 10.
        df_agg:           Per-point aggregation DataFrame from Module 10.
        trigger_results:  Anchor detection results from Module 04.
        census:           Positive-point census from Module 05.
        descent_windows:  Descent windows from Module 06.
        marker_orders:    Per-visit marker detection orders from Module 03.
        config:           CpmIaConfig with output paths and label suffixes.
        run_dt:           Pipeline start datetime (UTC) for the report header.

    Returns:
        Path of the compiled PDF report.

    Raises:
        ReportError: if the LaTeX template is missing, if pdflatex is not on
                     PATH, if compilation fails, or if the PDF already exists (G-10).
    """
    if not _TEMPLATE_PATH.exists():
        raise ReportError(f"LaTeX template not found: {_TEMPLATE_PATH}")

    if not shutil.which("pdflatex"):
        raise ReportError(
            "pdflatex not found on PATH. Install TeX Live or equivalent "
            "and ensure pdflatex is accessible."
        )

    output_dir = Path(config.output_path)
    report_stem = config.output_label_detail.removesuffix("_detail") + "_report"
    tex_path = output_dir / f"{report_stem}.tex"
    pdf_path = output_dir / f"{report_stem}.pdf"

    if pdf_path.exists():
        raise ReportError(f"Report PDF already exists (G-10): {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    values = _build_values(
        df_detail, df_agg, trigger_results, census,
        descent_windows, marker_orders, config, run_dt,
    )
    filled = _fill_template(template, values)
    tex_path.write_text(filled, encoding="utf-8")
    logger.debug("CPM-IA report .tex written | path=%s", tex_path)

    # Two pdflatex passes — required for correct TOC page numbers.
    _run_pdflatex(tex_path, output_dir)
    _run_pdflatex(tex_path, output_dir)

    # Remove auxiliary files produced by pdflatex.
    for ext in (".aux", ".log", ".out", ".toc"):
        aux = output_dir / f"{report_stem}{ext}"
        if aux.exists():
            aux.unlink()

    if not pdf_path.exists():
        raise ReportError(f"PDF not found after compilation: {pdf_path}")

    logger.info("CPM-IA report compiled | pdf=%s", pdf_path)
    return pdf_path
