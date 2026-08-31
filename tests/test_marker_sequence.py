# LINKED-TO: [REQ-CPM-IA-P26.0003]
"""Unit tests for src/marker_sequence.py — TC-03-001 through TC-03-008."""

import math
from typing import Any

import pandas as pd
import pytest

from src.data_ingestion import (
    COL_MARKER,
    COL_POINT,
    COL_RAW_VARIATION,
    COL_VISIT,
    COL_VISIT_DATE,
)
from src.marker_sequence import SequenceError, build_sequences

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df(**rows: Any) -> pd.DataFrame:
    """Build a minimal valid DataFrame from keyword columns."""
    base = {
        COL_VISIT: rows.get("visit", []),
        COL_MARKER: rows.get("marker", []),
        COL_POINT: rows.get("point", []),
        COL_RAW_VARIATION: rows.get("value", []),
        COL_VISIT_DATE: rows.get("date", ["2026-01-01"] * len(rows.get("visit", []))),
    }
    return pd.DataFrame(base)


def _isnan(v: float) -> bool:
    return math.isnan(v)


# ---------------------------------------------------------------------------
# TC-03-001 — Marker order follows first-appearance in row order (M1, M2, M3)
# ---------------------------------------------------------------------------

def test_tc_03_001_order_preserves_row_appearance() -> None:
    """Markers appear in rows as M1, M2, M3 — order must be [M1, M2, M3]."""
    df = _df(
        visit=["V1", "V1", "V1"],
        marker=["M1", "M2", "M3"],
        point=["P1", "P1", "P1"],
        value=[100.0, 200.0, 300.0],
    )
    order, _ = build_sequences(df)
    assert order["V1"] == ["M1", "M2", "M3"]


def test_tc_03_001_sequence_aligned_to_order() -> None:
    """Sequence values must align with marker_order positions."""
    df = _df(
        visit=["V1", "V1", "V1"],
        marker=["M1", "M2", "M3"],
        point=["P1", "P1", "P1"],
        value=[100.0, 200.0, 300.0],
    )
    order, seqs = build_sequences(df)
    assert seqs[("V1", "P1")] == [100.0, 200.0, 300.0]


# ---------------------------------------------------------------------------
# TC-03-002 — First appearances: M2, M1, M3 → order is [M2, M1, M3]
# ---------------------------------------------------------------------------

def test_tc_03_002_order_reflects_first_row_of_each_marker() -> None:
    """M2 first appears before M1 in row order — must be [M2, M1, M3]."""
    df = _df(
        visit=["V1", "V1", "V1"],
        marker=["M2", "M1", "M3"],
        point=["P1", "P1", "P1"],
        value=[200.0, 100.0, 300.0],
    )
    order, _ = build_sequences(df)
    assert order["V1"] == ["M2", "M1", "M3"]


def test_tc_03_002_not_alphabetically_sorted() -> None:
    """Confirm the order is NOT simply alphabetical — M2 before M1 is correct here."""
    df = _df(
        visit=["V1", "V1"],
        marker=["M2", "M1"],
        point=["P1", "P1"],
        value=[200.0, 100.0],
    )
    order, _ = build_sequences(df)
    assert order["V1"][0] == "M2"
    assert order["V1"][1] == "M1"


# ---------------------------------------------------------------------------
# TC-03-003 — Missing marker for a (visit, point) pair fills with NaN
# ---------------------------------------------------------------------------

def test_tc_03_003_missing_marker_fills_nan() -> None:
    """(V1, P2) has only M1; M2 position in its sequence must be NaN."""
    df = _df(
        visit=["V1", "V1", "V1"],
        marker=["M1", "M2", "M1"],
        point=["P1", "P1", "P2"],
        value=[100.0, 200.0, 150.0],
    )
    order, seqs = build_sequences(df)
    assert order["V1"] == ["M1", "M2"]
    assert seqs[("V1", "P1")] == [100.0, 200.0]
    assert seqs[("V1", "P2")][0] == 150.0
    assert _isnan(seqs[("V1", "P2")][1])


def test_tc_03_003_per_visit_sequence_length_matches_visit_protocol() -> None:
    """V2 protocol has only M1; (V2, P2) sequence length is 1 (not padded with NaN for V1-only M2)."""
    # V1 tests M1 and M2; V2 tests only M1.
    # Under per-visit ordering each visit's sequences are aligned solely to that
    # visit's detected markers — V2 sequences have no slot for M2.
    df = _df(
        visit=["V1", "V1", "V2"],
        marker=["M1", "M2", "M1"],
        point=["P1", "P1", "P2"],
        value=[100.0, 200.0, 50.0],
    )
    order, seqs = build_sequences(df)
    assert order["V1"] == ["M1", "M2"]
    assert order["V2"] == ["M1"]
    # (V2, P2): aligned to V2's order ["M1"] → length 1, value 50.0
    assert len(seqs[("V2", "P2")]) == 1
    assert seqs[("V2", "P2")][0] == 50.0


# ---------------------------------------------------------------------------
# TC-03-004 — Duplicate (visit, point, marker) triplet raises SequenceError
# ---------------------------------------------------------------------------

def test_tc_03_004_conflicting_triplet_raises() -> None:
    """(V1, P1, M1) with two different values raises SequenceError."""
    df = _df(
        visit=["V1", "V1"],
        marker=["M1", "M1"],
        point=["P1", "P1"],
        value=[100.0, 200.0],
    )
    with pytest.raises(SequenceError, match="Conflicting values"):
        build_sequences(df)


def test_tc_03_004_conflicting_error_contains_row_index() -> None:
    """SequenceError message must contain the row index of the conflicting record."""
    df = _df(
        visit=["V1", "V1", "V1"],
        marker=["M1", "M2", "M1"],
        point=["P1", "P1", "P1"],
        value=[100.0, 200.0, 999.0],
    )
    with pytest.raises(SequenceError, match=r"row \d+"):
        build_sequences(df)


def test_tc_03_004_conflict_in_one_group_does_not_affect_others() -> None:
    """Conflict in (V1, P1) raises before processing (V1, P2) — no silent partial result."""
    df = _df(
        visit=["V1", "V1", "V1", "V1"],
        marker=["M1", "M1", "M1", "M2"],
        point=["P1", "P1", "P2", "P2"],
        value=[100.0, 200.0, 150.0, 250.0],
    )
    with pytest.raises(SequenceError):
        build_sequences(df)


# ---------------------------------------------------------------------------
# TC-03-005 — Empty DataFrame raises SequenceError
# ---------------------------------------------------------------------------

def test_tc_03_005_empty_dataframe_raises() -> None:
    """Empty DataFrame raises SequenceError with descriptive message."""
    df = pd.DataFrame(
        columns=[COL_VISIT, COL_MARKER, COL_POINT, COL_RAW_VARIATION, COL_VISIT_DATE]
    )
    with pytest.raises(SequenceError, match="Empty input dataset"):
        build_sequences(df)


# ---------------------------------------------------------------------------
# TC-03-006 — Single row produces single-element order and sequence
# ---------------------------------------------------------------------------

def test_tc_03_006_single_row() -> None:
    """Single data row: marker_order has one element; sequence list has one value."""
    df = _df(visit=["V1"], marker=["M1"], point=["P1"], value=[150.0])
    order, seqs = build_sequences(df)
    assert order == {"V1": ["M1"]}
    assert seqs == {("V1", "P1"): [150.0]}


# ---------------------------------------------------------------------------
# TC-03-007 — marker_order applied consistently across all (visit, point) pairs
# ---------------------------------------------------------------------------

def test_tc_03_007_consistent_index_to_marker_mapping() -> None:
    """Index i in every sequence must map to marker_order[i] for all pairs."""
    df = _df(
        visit=["V1", "V1", "V2", "V2", "V1", "V2"],
        marker=["M1", "M2", "M2", "M1", "M3", "M3"],
        point=["P1", "P1", "P1", "P1", "P1", "P1"],
        value=[100.0, 200.0, 210.0, 110.0, 300.0, 310.0],
    )
    # V1 first appearances: M1 (row 0), M2 (row 1), M3 (row 4)
    # V2 first appearances: M2 (row 2), M1 (row 3), M3 (row 5)
    order, seqs = build_sequences(df)
    assert order["V1"] == ["M1", "M2", "M3"]
    assert order["V2"] == ["M2", "M1", "M3"]

    # For every pair, verify value at index i corresponds to that visit's order[i]
    for (visit, point), seq in seqs.items():
        visit_order = order[visit]
        assert len(seq) == len(visit_order)
        for i, marker in enumerate(visit_order):
            mask = (
                (df[COL_VISIT] == visit)
                & (df[COL_POINT] == point)
                & (df[COL_MARKER] == marker)
            )
            if mask.any():
                expected = float(df.loc[mask, COL_RAW_VARIATION].iloc[0])
                assert seq[i] == expected
            else:
                assert _isnan(seq[i])


# ---------------------------------------------------------------------------
# TC-03-008 — Full mock structure (2 visits x 4 markers x 2 points, no missing)
# ---------------------------------------------------------------------------

def test_tc_03_008_full_mock_no_missing_values() -> None:
    """2 visits x 4 markers x 2 points: 4 sequences per visit, all length 4, no NaN."""
    rows = []
    for v in ["V001", "V002"]:
        for p in ["P01", "P02"]:
            for m in ["M1", "M2", "M3", "M4"]:
                rows.append({COL_VISIT: v, COL_MARKER: m, COL_POINT: p,
                              COL_RAW_VARIATION: 100.0, COL_VISIT_DATE: "2026-01-01"})
    df = pd.DataFrame(rows)

    order, seqs = build_sequences(df)
    assert order["V001"] == ["M1", "M2", "M3", "M4"]
    assert order["V002"] == ["M1", "M2", "M3", "M4"]
    assert len(seqs) == 4  # 2 visits x 2 points
    for seq in seqs.values():
        assert len(seq) == 4
        assert not any(_isnan(v) for v in seq)


# ---------------------------------------------------------------------------
# TC-03-008 — Exact duplicate rows are silently removed
# ---------------------------------------------------------------------------

def test_tc_03_008_exact_duplicates_dropped_silently() -> None:
    """Rows with identical (visit, point, marker, value) are dropped; result is correct."""
    rows = [
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: 100.0, COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M2", COL_POINT: "P1", COL_RAW_VARIATION: 200.0, COL_VISIT_DATE: "2026-01-01"},
        # exact duplicate of the first row — must be dropped silently
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: 100.0, COL_VISIT_DATE: "2026-01-01"},
    ]
    df = pd.DataFrame(rows)
    order, seqs = build_sequences(df)
    assert order["V1"] == ["M1", "M2"]
    assert seqs[("V1", "P1")] == [100.0, 200.0]


def test_tc_03_008_exact_duplicate_nan_dropped_silently() -> None:
    """Exact duplicate rows where both values are NaN are also removed silently."""
    rows = [
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: float("nan"), COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M2", COL_POINT: "P1", COL_RAW_VARIATION: 200.0, COL_VISIT_DATE: "2026-01-01"},
        # exact duplicate NaN row
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: float("nan"), COL_VISIT_DATE: "2026-01-01"},
    ]
    df = pd.DataFrame(rows)
    order, seqs = build_sequences(df)
    assert _isnan(seqs[("V1", "P1")][0])
    assert seqs[("V1", "P1")][1] == 200.0


# ---------------------------------------------------------------------------
# TC-03-009 — Conflicting values raise SequenceError
# ---------------------------------------------------------------------------

def test_tc_03_009_conflicting_values_raise_error() -> None:
    """Same (visit, point, marker) with different values raises SequenceError."""
    rows = [
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: 100.0, COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: 999.0, COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M2", COL_POINT: "P1", COL_RAW_VARIATION: 200.0, COL_VISIT_DATE: "2026-01-01"},
    ]
    df = pd.DataFrame(rows)
    with pytest.raises(SequenceError, match="Conflicting values"):
        build_sequences(df)


def test_tc_03_009_conflict_nan_vs_value_raises_error() -> None:
    """Same (visit, point, marker) with NaN in one row and a number in another raises SequenceError."""
    rows = [
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: float("nan"), COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M1", COL_POINT: "P1", COL_RAW_VARIATION: 50.0, COL_VISIT_DATE: "2026-01-01"},
        {COL_VISIT: "V1", COL_MARKER: "M2", COL_POINT: "P1", COL_RAW_VARIATION: 200.0, COL_VISIT_DATE: "2026-01-01"},
    ]
    df = pd.DataFrame(rows)
    with pytest.raises(SequenceError, match="Conflicting values"):
        build_sequences(df)
