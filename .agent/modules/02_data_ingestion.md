# Module 02 — Data Ingestion
**File:** `src/data_ingestion.py`
**SR:** REQ-CPM-IA-P26.0002 — Autonomous Raw-Variation Ingestion
**Linked GR:** REQ-G-P26.0031
**Status:** Complete — 2026-08-27 | 15/15 tests pass

---

## Requirement (verbatim)

The component operate autonomously on the consolidated raw percentage-variation dataset produced by the Raw Variation Computation component, ingesting it as a long-format table in which every record identifies a visit, a marker and an anatomical point, together with its raw percentage variation and the associated visit metadata. The component validates the presence of the required fields and doesn't require input from any other component to complete its computation.

---

## Functional Boundary

This module reads the input file from the path provided by `CpmIaConfig.input_path`, validates its schema, and returns a clean `pandas.DataFrame` in the expected long format. It performs no analytical computation.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `config` | `CpmIaConfig` | Configuration object from Module 01 (provides `input_path`). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `df` | `pd.DataFrame` | Validated long-format DataFrame ready for downstream modules. |

---

## Required Columns

The following columns must be present in the input file (exact names defined here as constants in this module):

| Column Constant | Expected Semantics |
|-----------------|--------------------|
| `COL_VISIT` | Visit identifier |
| `COL_MARKER` | Marker identifier |
| `COL_POINT` | Anatomical point identifier |
| `COL_RAW_VARIATION` | Raw percentage variation (numeric) |
| `COL_VISIT_METADATA_*` | One or more visit metadata columns (validated by presence of at least one `visit_date` or equivalent field — exact names to be confirmed against upstream component schema) |

---

## Behaviour Specification

1. Read the file at `config.input_path`. Supported format: CSV (comma-separated, UTF-8). If the extension does not match, raise `IngestionError`.
2. Verify that all required columns listed above are present. If any are missing, raise `IngestionError` naming the absent columns.
3. Cast `COL_RAW_VARIATION` to `float64`; raise `IngestionError` if any value cannot be cast.
4. Drop no rows silently; if NaN values appear in key columns (`COL_VISIT`, `COL_MARKER`, `COL_POINT`), raise `IngestionError` with row indices.
5. Log row count, column list, and unique visit/marker/point counts at INFO level.
6. Return the validated DataFrame.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Input file not found | Raise `IngestionError("Input file not found: <path>")`, abort. |
| Unsupported file format | Raise `IngestionError("Unsupported input format: <ext>")`, abort. |
| Required column missing | Raise `IngestionError("Missing required column(s): <list>")`, abort. |
| Non-numeric variation values | Raise `IngestionError("Non-numeric values in COL_RAW_VARIATION")`, abort. |
| NaN in key identifier columns | Raise `IngestionError("NaN in key columns at rows: <indices>")`, abort. |

---

## Guardrails Enforced

- G-03: All field validation occurs in this module before any computation starts.

---

## Test File

`tests/test_data_ingestion.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-02-001 | Valid CSV with all required columns | Returns DataFrame with correct dtypes. |
| TC-02-002 | CSV missing `COL_MARKER` | Raises `IngestionError` naming `COL_MARKER`. |
| TC-02-003 | `COL_RAW_VARIATION` contains string "N/A" | Raises `IngestionError`. |
| TC-02-004 | NaN in `COL_VISIT` | Raises `IngestionError` with row indices. |
| TC-02-005 | File not found | Raises `IngestionError`. |
