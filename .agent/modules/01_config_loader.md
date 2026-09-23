# Module 01 — Config Loader
**File:** `src/config_loader.py`
**SR:** REQ-CPM-IA-P26.0001 — External Configuration Loading
**Linked GR:** REQ-G-P26.0072
**Status:** Complete — 2026-09-23 | 21/21 tests pass

---

## Requirement (verbatim)

The component loads all execution parameters at runtime from an external XML configuration file, with no processing parameter hardcoded in the source. The configuration provides, as a minimum: the input source definition and output paths; the positive-detection threshold (required); the rise tolerance ε; the maximum descent window length N_max; and a data-quality policy flag. A missing or malformed configuration file results in a controlled failure of the run.

---

## Functional Boundary

This module is the **sole** entry point for all runtime parameters. It is called once at process start by `main.py` and returns a validated configuration object used by every downstream module. It must not contain any analytical logic.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `config_path` | `str` / `Path` | Absolute or relative path to the XML configuration file. |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `config` | `CpmIaConfig` | Immutable frozen dataclass containing all runtime parameters. |

### CpmIaConfig fields

| Field | Type | Description |
|-------|------|-------------|
| `input` | `InputConfig` | Input source definition (type + source-specific params). |
| `output_path` | `Path` | Directory for output files. |
| `output_label_detail` | `str` | Stem for the detail CSV filename. |
| `output_label_aggregated` | `str` | Stem for the aggregated CSV filename. |
| `threshold_pct` | `float` | Positive-detection threshold — **required** (absence → ConfigurationError). |
| `rise_tolerance_epsilon` | `float` | Rise tolerance for descent window closure. |
| `n_max` | `int` | Maximum descent window length per anchor. |
| `data_quality` | `DataQualityConfig` | Data-quality policy (`drop_invalid_points: bool`). |

### InputConfig and sub-dataclasses

```
InputConfig
  .type: str                   # 'csv' | 'excel' | 'db'
  .csv: Optional[CsvInputConfig]
        .path: Path
  .excel: Optional[ExcelInputConfig]
          .files: Tuple[ExcelFileConfig, ...]
                  .path: Path
                  .visit_id: str
                  .visit_date: str
  .db: Optional[DbInputConfig]
       .dsn_env: str
       .query: str
```

`CpmIaConfig.input_description() -> str` returns a human-readable string for logging/reporting.

---

## Behaviour Specification

1. Parse the XML file at `config_path`. Raise `ConfigurationError` if file is absent or malformed.
2. Determine input source:
   - If `<input>` block present → parse `<type>`, populate the corresponding sub-dataclass.
   - If `<input>` absent but `<input_path>` present → backward-compat: create `InputConfig(type='csv', csv=CsvInputConfig(path=...))`.
   - If neither → raise `ConfigurationError`.
3. Parse `threshold_pct` as **required** float. Absent or blank → raise `ConfigurationError` (no silent default).
4. Parse `rise_tolerance_epsilon` and `n_max` as required.
5. Parse `<data_quality><drop_invalid_points>` as bool; default `True` if block absent.
6. Return fully populated `CpmIaConfig`.

---

## Guardrails Enforced

- G-01: All parameters from XML; no processing parameter hard-coded.
- G-02: Missing or malformed config → controlled failure.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| File not found | Raise `ConfigurationError("Config file not found: <path>")`. |
| Malformed XML | Raise `ConfigurationError("Malformed XML in config: <path>")`. |
| `threshold_pct` absent | Raise `ConfigurationError("Missing required config element: <threshold_pct>")`. |
| Invalid numeric value | Raise `ConfigurationError("Invalid value for <tag>: expected <type>")`. |

---

## Test File

`tests/test_config_loader.py` — 21 tests

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-01-001 | Valid XML with new `<input>` block (type=csv) | Returns correct CpmIaConfig. |
| TC-01-002 | Valid XML with legacy `<input_path>` | Backward-compat: returns CpmIaConfig with InputConfig(type='csv'). |
| TC-01-003 | `<threshold_pct>` absent | Raises ConfigurationError. |
| TC-01-004 | `<threshold_pct>` with non-numeric value | Raises ConfigurationError. |
| TC-01-005 | File not found | Raises ConfigurationError. |
| TC-01-006 | Malformed XML | Raises ConfigurationError. |
| TC-01-007 | Valid XML with type=excel; two `<file>` entries | ExcelInputConfig with 2 ExcelFileConfig entries. |
| TC-01-008 | `<data_quality>` absent | DataQualityConfig(drop_invalid_points=True). |
| TC-01-009 | `<data_quality><drop_invalid_points>false` | DataQualityConfig(drop_invalid_points=False). |
