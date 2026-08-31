# LINKED-TO: [REQ-CPM-IA-P26.0003]
"""
marker_sequence.py — Marker Sequence Reconstruction for the CPM-IA component.

Derives the per-visit canonical marker order (order of first appearance within
each visit) and builds per-(visit, point) ordered value sequences aligned to that
per-visit order. This preserves the temporal detection order within each visit,
which is required for correct cross-marker influence attribution (G-04).
Produces no analytical output — prepares the analysis axis for Modules 04-09.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import pandas as pd

from src.data_ingestion import COL_MARKER, COL_POINT, COL_RAW_VARIATION, COL_VISIT

logger = logging.getLogger(__name__)

# Per-visit marker order: visit_id -> list of marker identifiers in detection order.
# Each visit maintains its own independent ordering; sequences are aligned to it.
PerVisitMarkerOrders = Dict[str, List[str]]
Sequences = Dict[Tuple[str, str], List[float]]


class SequenceError(Exception):
    """Raised when marker sequence reconstruction fails."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_sequences(df: pd.DataFrame) -> Tuple[PerVisitMarkerOrders, Sequences]:
    """
    Derive per-visit marker orders and build per-(visit, point) sequences.

    Args:
        df: Validated long-format DataFrame from load_data().

    Returns:
        per_visit_orders: mapping visit_id -> marker list in temporal detection order.
                          Order is the first-appearance order of markers within each
                          visit's rows (G-04). Visits with different detection orders
                          each maintain their own independent ordering.
        sequences: mapping (visit_id, point_id) -> list[float] aligned to that
                   visit's per_visit_orders entry.
                   float('nan') fills positions where a marker is in the visit's
                   protocol but has no recorded value for that specific (visit, point).

    Raises:
        SequenceError: on empty input or any (visit, point, marker) triplet with
                       conflicting (different) values. Exact duplicate rows are
                       silently removed before sequence construction.
    """
    if df.empty:
        raise SequenceError("Empty input dataset; cannot derive marker order")

    # Step 1 — remove exact duplicate rows (same visit, point, marker, and value).
    # pandas drop_duplicates treats NaN as equal to NaN, so rows where all four
    # columns match — including both-NaN value pairs — are correctly collapsed.
    n_before = len(df)
    df = df.drop_duplicates(subset=[COL_VISIT, COL_MARKER, COL_POINT, COL_RAW_VARIATION])
    n_dropped = n_before - len(df)
    if n_dropped:
        logger.warning(
            "Removed %d exact duplicate (visit, point, marker) rows before sequence build",
            n_dropped,
        )

    # Step 2 — derive per-visit marker order (G-04).
    # dict.fromkeys() walks the visit's rows in their original order and deduplicates
    # while preserving first-appearance position within each visit. Never substitute
    # sorted(), set(), or .unique() here — those destroy temporal ordering.
    per_visit_orders: PerVisitMarkerOrders = {}
    for visit, grp in df.groupby(COL_VISIT, sort=False):
        per_visit_orders[str(visit)] = list(dict.fromkeys(grp[COL_MARKER]))

    # Step 3 — build per-(visit, point) sequences aligned to per-visit detection order.
    # After exact-dup removal any remaining duplicate marker within a group has a
    # different value — that is a data conflict and must raise an error.
    # sort=False: group discovery order follows the DataFrame row order.
    sequences: Sequences = {}
    for (visit, point), group in df.groupby([COL_VISIT, COL_POINT], sort=False):
        dup_mask = group[COL_MARKER].duplicated(keep=False)
        if dup_mask.any():
            first_dup_idx = int(group.index[dup_mask][0])
            raise SequenceError(
                f"Conflicting values for (visit, point, marker) at row {first_dup_idx}: "
                f"same triplet appears with different percentage_variation values"
            )

        visit_marker_order = per_visit_orders[str(visit)]
        marker_to_val: dict[str, float] = dict(
            zip(group[COL_MARKER], group[COL_RAW_VARIATION])
        )
        sequences[(str(visit), str(point))] = [
            marker_to_val.get(m, float("nan")) for m in visit_marker_order
        ]

    logger.debug(
        "CPM-IA marker orders derived | visits=%d | (visit, point) pairs=%d",
        len(per_visit_orders),
        len(sequences),
    )

    return per_visit_orders, sequences
