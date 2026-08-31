# CLAUDE.md — Cross Points and Markers Influence Analysis

> Project memory for Claude Code. Operative under SOP #L001-U015-P26.0141 (Agentic Development WorkFlow).
> The `math-b-agentic-workflow` plugin already injects the full guardrails at session start; this file holds component-specific context.

## Component
- Name: Cross Points and Markers Influence Analysis
- Initials (ID prefix): CPM-IA
- SR&TS doc ID: #L001-U015-P26.0127 — Rev 00.00 (26 August 2026)
- MDR class / scope notes: Class I — non-invasive bioelectrical surface current acquisition; non-diagnostic language applies throughout

## Workflow reminders
- Module-by-module only. Plan mode first, HALT on ambiguity, wait for explicit approval before coding.
- Every source file carries `# LINKED-TO: [REQ-CPM-IA-P26.XXXX]` anchors (enforced by PreToolUse:Write hook).
- Unit-test each module (Step 4); formal verification is independent and evidence-based (Step 5).

## AI Generation Record (audit trail)
> Recommended for ISO 13485 traceability — log who/what generated and verified each module.

| Date | Module | Model + version | Operator [acronym] | Approved by |
| :--- | :----- | :-------------- | :----------------- | :---------- |
| 2026-08-27 | `src/config_loader.py` + `tests/test_config_loader.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/data_ingestion.py` + `tests/test_data_ingestion.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/marker_sequence.py` + `tests/test_marker_sequence.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/trigger_detection.py` + `tests/test_trigger_detection.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/positive_census.py` + `tests/test_positive_census.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/descent_window.py` + `tests/test_descent_window.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/descent_slope.py` + `tests/test_descent_slope.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/descent_descriptors.py` + `tests/test_descent_descriptors.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/variance_indicator.py` + `tests/test_variance_indicator.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/output_consolidation.py` + `tests/test_output_consolidation.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-27 | `src/main.py` + `tests/test_main.py` | claude-sonnet-4-6 | [IR] |  |
| 2026-08-31 | Fix: per-visit marker order (`src/marker_sequence.py`, `src/trigger_detection.py`, `src/main.py`) + tests | claude-sonnet-4-6 | [IR] |  |
| 2026-08-31 | Add `variance_ratio` field (`src/variance_indicator.py`, `src/output_consolidation.py`) + tests TC-09-010 | claude-sonnet-4-6 | [IR] |  |
| 2026-08-31 | M11: `src/report_generator.py` + `data/templates/cpm_ia_report.tex.template` + `tests/test_report_generator.py` (TC-11-001–018) | claude-sonnet-4-6 | [IR] |  |

## Component-specific rules

### Data schema (input)
Long-format CSV, UTF-8, comma-separated. Required columns: visit id, marker id, anatomical point id, raw percentage variation (float64), plus visit metadata column(s). Exact column names are constants defined in `src/data_ingestion.py`.

### Key parameters (all from XML config — never hardcode)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `threshold_pct` | 300.0 | Positive-detection threshold (%) |
| `rise_tolerance_epsilon` | — | Tolerance to close descent window |
| `n_max` | — | Maximum descent window length |

### Immutability criteria
- Marker order derived once **per visit** at ingestion (order of first appearance within each visit's rows) — immutable for the entire run.
- Anchor = first threshold-crossing marker per (visit, point) series — reassignment during a run is forbidden.

### Module execution order
config_loader → data_ingestion → marker_sequence → trigger_detection → positive_census → descent_window → descent_slope → descent_descriptors → variance_indicator → output_consolidation → report_generator
