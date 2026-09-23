# Module 02 — Data Ingestion
**File:** `src/data_ingestion.py`
**SR:** REQ-CPM-IA-P26.0002 — Autonomous Raw-Variation Ingestion
**Linked GR:** REQ-G-P26.0031
**Status:** Complete — 2026-09-23 | 20/20 tests pass

---

## Requirement (verbatim)

The component operates autonomously on the consolidated raw percentage-variation dataset produced by the Raw Variation Computation component, ingesting it as a long-format table in which every record identifies a visit, a marker and an anatomical point, together with its raw percentage variation and the associated visit metadata. The component validates the presence of the required fields and doesn't require input from any other component to complete its computation.

---

## Functional Boundary

This module dispatches to the appropriate `DataSource` implementation based on `config.input.type`, loads data into a validated long-format DataFrame, applies data-quality filtering, and returns both the clean DataFrame and a data quality report. It performs no analytical computation.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `config` | `CpmIaConfig` | Configuration object from Module 01. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `df` | `pd.DataFrame` | Validated long-format DataFrame ready for downstream modules. |
| `dq_report` | `DataQualityReport` | Summary of data-quality actions taken during ingestion. |

Both are returned as a tuple `(df, dq_report)`.

---

## DataSource Abstraction

| Class | Behaviour |
|-------|-----------|
| `CsvSource` | Reads a UTF-8 long-format CSV; raises `IngestionError` if extension is not `.csv`. |
| `ExcelSource` | For each `ExcelFileConfig`: reads the wide xlsx with openpyxl; first column = marker identifiers; remaining columns = anatomical point names; melts to long format; adds `visit_id` and `visit_date` from config. Ignores columns with None/empty headers. Concatenates all files. |
| `PostgresSource` | Stub: raises `IngestionError("Postgres source not configured: …")`. Import of psycopg is lazy (try/except ImportError) so offline use is unaffected. |

---

## Required Columns (long format)

| Column constant | Name | Semantics |
|-----------------|------|-----------|
| `COL_VISIT` | `visit_id` | Visit identifier |
| `COL_MARKER` | `marker` | Marker identifier |
| `COL_POINT` | `point` | Anatomical point identifier |
| `COL_RAW_VARIATION` | `percentage_variation` | Raw percentage variation (numeric) |
| `COL_VISIT_DATE` | `visit_date` | Visit date (string, no datetime parsing) |

---

## DataQualityReport fields

| Field | Description |
|-------|-------------|
| `total_rows` | Total rows after source load, before quality filtering |
| `rows_dropped_empty_keys` | Rows dropped due to empty/whitespace visit_id/marker/point |
| `invalid_point_names` | Tuple of unique point name strings that failed pattern validation |
| `rows_affected_invalid_points` | Rows dropped (if drop_mode=True) or warned |
| `drop_mode` | True if invalid rows were dropped; False if only warned |

---

## Valid Point Name Patterns

A point is valid if it matches at least one of:
- **New format (4 components):** `^[LR][HF]\s*-\s*\d+\s*-\s*\S+\s*-\s*.+` (e.g. `LH - 2 - i - colon`)
- **Short format (3 components):** `^[LR][HF]\s*-\s*\d+\s*-\s*\S+` (e.g. `LH - 3 - c`) — 4th component optional
- **Legacy format:** `.+\s*\[\d+\]\s*$` (e.g. `SomeName [3]`)

Non-matching, non-empty points are invalid. Behaviour controlled by `config.data_quality.drop_invalid_points`.

---

## Behaviour Specification

1. Dispatch on `config.input.type` → instantiate appropriate `DataSource`; call `.load()`.
2. Verify all required columns present; raise `IngestionError` if any missing.
3. Cast `COL_RAW_VARIATION` to float64; raise `IngestionError` for non-numeric non-NaN values.
4. Drop rows with empty/whitespace in key columns; count in `rows_dropped_empty_keys`.
5. Validate point names against patterns; drop or warn based on `drop_invalid_points`.
6. Raise `IngestionError` if NaN remains in key identifier columns after filtering.
7. Log data-quality summary at INFO/WARNING level.
8. Return `(df_clean, DataQualityReport)`.

---

## Guardrails Enforced

- G-03: All field validation before any computation.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| Input file not found | Raise `IngestionError("Input file not found: <path>")`. |
| Unsupported file format (CSV source) | Raise `IngestionError("Unsupported input format: <ext>")`. |
| Required column missing | Raise `IngestionError("Missing required column(s): <list>")`. |
| Non-numeric variation values | Raise `IngestionError("Non-numeric values in percentage_variation")`. |
| NaN in key identifier columns (post-filter) | Raise `IngestionError("NaN in key columns at rows: <indices>")`. |
| Postgres source: DSN not configured | Raise `IngestionError("Postgres source not configured: …")`. |

---

## Test File

`tests/test_data_ingestion.py` — 17 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-02-001 | Valid CSV with all required columns | Returns (DataFrame, DataQualityReport) with correct dtypes. |
| TC-02-002 | CSV missing `marker` | Raises IngestionError naming missing column. |
| TC-02-003 | `percentage_variation` contains string "N/A" | Raises IngestionError. |
| TC-02-004 | NaN in `visit_id` | Raises IngestionError with row indices. |
| TC-02-005 | File not found | Raises IngestionError. |
| TC-02-006 | ExcelSource: wide xlsx → correct long DataFrame | visit_id/visit_date from config; point columns melted correctly. |
| TC-02-007 | ExcelSource: column "ciao" excluded (invalid point) | Dropped with WARNING when drop_invalid_points=True. |
| TC-02-008 | drop_invalid_points=False | Invalid point rows kept; WARNING logged; DataQualityReport reflects warn mode. |
| TC-02-009 | PostgresSource not configured | Raises IngestionError. |
| TC-02-011 | Point name `LH - 3 - c` (3 components) | Accepted as valid; no rows dropped. |
| TC-02-011 | Point name `LH - 3` (2 components) | Rejected as invalid. |
| TC-02-011 | Point name `LH - 5 - e - Small intestine` (4 components) alongside 3-component | Both accepted. |
