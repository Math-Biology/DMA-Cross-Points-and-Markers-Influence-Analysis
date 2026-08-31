# Module 01 — Config Loader
**File:** `src/config_loader.py`
**SR:** REQ-CPM-IA-P26.0001 — External Configuration Loading
**Linked GR:** REQ-G-P26.0072
**Status:** Complete — 2026-08-27 | 13/13 tests pass

---

## Requirement (verbatim)

The component loads all execution parameters at runtime from an external XML configuration file, with no processing parameter hardcoded in the source. The configuration provides, as a minimum: the input and output paths and the output-label suffixes; the positive-detection threshold (default 300 %); the rise tolerance ε used to close a descent window; and the maximum number of descent points N_max. A missing or malformed configuration file results in a controlled failure of the run.

---

## Functional Boundary

This module is the **sole** entry point for all runtime parameters. It is called once at process start by `main.py` and returns a validated configuration object used by every downstream module. It must not contain any analytical logic.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `config_path` | `str` / `Path` | Absolute or relative path to the XML configuration file (passed as CLI argument or default location). |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `CpmIaConfig` | dataclass / named object | Validated configuration object carrying all parameters listed below. |

### Minimum fields in `CpmIaConfig`

| Field | XML Element | Type | Default |
|-------|-------------|------|---------|
| `input_path` | `<input_path>` | `Path` | — (required) |
| `output_path` | `<output_path>` | `Path` | — (required) |
| `output_label_detail` | `<output_label_detail>` | `str` | — (required) |
| `output_label_aggregated` | `<output_label_aggregated>` | `str` | — (required) |
| `threshold_pct` | `<threshold_pct>` | `float` | 300.0 |
| `rise_tolerance_epsilon` | `<rise_tolerance_epsilon>` | `float` | — (required) |
| `n_max` | `<n_max>` | `int` | — (required) |

---

## Behaviour Specification

1. Parse the XML file at `config_path` using the standard library (`xml.etree.ElementTree`).
2. For each required field: if the element is absent or its text cannot be cast to the declared type, raise a descriptive `ConfigurationError` and abort — do not fall back to silent defaults for required fields.
3. For `threshold_pct`: if the element is absent, use the default 300.0; if present but malformed, raise `ConfigurationError`.
4. Return the fully populated `CpmIaConfig` object.
5. Log the resolved configuration at INFO level (paths, threshold, ε, N_max) before returning.

---

## Error Conditions

| Condition | Behaviour |
|-----------|-----------|
| File not found | Raise `ConfigurationError("Config file not found: <path>")`, abort run. |
| File not valid XML | Raise `ConfigurationError("Malformed XML in config: <path>")`, abort run. |
| Required element missing | Raise `ConfigurationError("Missing required config element: <tag>")`, abort run. |
| Type cast failure | Raise `ConfigurationError("Invalid value for <tag>: expected <type>")`, abort run. |

---

## Guardrails Enforced

- G-01: This module is the exclusive location where parameters are read; no other module may read config files.
- G-02: Any failure in config parsing must propagate as `ConfigurationError` to `main.py` which exits with a non-zero code.
- G-10: Output path uniqueness enforced by suffix fields; this module exposes the suffix but does not create files.

---

## Test File

`tests/test_config_loader.py`

### Test cases (minimum)

| ID | Scenario | Expected |
|----|----------|----------|
| TC-01-001 | Valid XML with all required fields | Returns `CpmIaConfig` with correct values. |
| TC-01-002 | Valid XML, `threshold_pct` absent | Returns `CpmIaConfig` with `threshold_pct = 300.0`. |
| TC-01-003 | File not found | Raises `ConfigurationError`. |
| TC-01-004 | Malformed XML (truncated) | Raises `ConfigurationError`. |
| TC-01-005 | Required element `n_max` missing | Raises `ConfigurationError`. |
| TC-01-006 | `n_max` present but non-integer value | Raises `ConfigurationError`. |
