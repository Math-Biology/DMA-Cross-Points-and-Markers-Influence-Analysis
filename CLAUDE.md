# CLAUDE.md — Cross Points and Markers Influence Analysis

> Project memory for Claude Code. Operative under SOP #L001-U015-P26.0141 (Agentic Development WorkFlow).
> The `math-b-agentic-workflow` plugin already injects the full guardrails at session start; this file holds component-specific context.

## Component
- Name: Cross Points and Markers Influence Analysis
- Initials (ID prefix): CPM-IA
- SR&TS doc ID: #L001-U015-P26.0127 — Rev 00.01 (23 September 2026)
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
| 2026-09-23 | Rev 00.01 — multi-anchor refactor (M01–M11 + all tests): ingestione flessibile csv/excel/db, `>=` soglia, tutti i positivi, `positives_count`, `window_close_reason`, nuova granularità output `(visita, punto, àncora)`, data quality report | claude-sonnet-4-6 | [IR] |  |

## Component-specific rules

### Data schema (input)
Flessibile — sorgente pilotata da `<input><type>csv|excel|db</type></input>` nella config XML:
- **csv**: long-format CSV, UTF-8, comma-separated
- **excel**: file wide (marker × punto); melt → long effettuato da `ExcelSource`; `visit_id`/`visit_date` dalla config
- **db**: stub Postgres predisposto (connessione via variabile d'ambiente `dsn_env`)

Colonne richieste nel formato long (costanti in `src/data_ingestion.py`): `visit_id`, `marker`, `point`, `percentage_variation` (float64), `visit_date`.

Punti anatomici validi:
- **Formato nuovo (4 componenti):** `^[LR][HF]\s*-\s*\d+\s*-\s*\S+\s*-\s*.+` (es. `LH - 2 - i - colon`)
- **Formato corto (3 componenti):** `^[LR][HF]\s*-\s*\d+\s*-\s*\S+` (es. `LH - 3 - c`) — 4° componente opzionale
- **Formato legacy:** `.+\s*\[\d+\]\s*$` (es. `SomeName [3]`)

Punti non conformi → scartati (WARNING) se `<drop_invalid_points>true</drop_invalid_points>`.

### Key parameters (all from XML config — never hardcode)
| Parameter | Valore corrente | Note |
|-----------|----------------|------|
| `threshold_pct` | 300.0 | **Obbligatorio** — assenza → `ConfigurationError`; positivo se valore `>=` soglia |
| `rise_tolerance_epsilon` | 1.0 | Da tarare in futuro |
| `n_max` | 1000 | Da tarare in futuro |

### Immutability criteria
- Marker order derived once **per visit** at ingestion (order of first appearance within each visit's rows) — immutable for the entire run.
- **Àncore multiple**: per ogni (visit, point), TUTTE le posizioni con valore `>= threshold_pct` sono registrate come àncore (in ordine di sequenza). Non esiste più "solo la prima"; il campo `anchors: List[Anchor]` contiene la lista completa.
- Una volta assegnata, la lista àncore di una serie è immutabile per il run.

### Output granularity (Rev 00.01)
- **`cpm_ia_detail.csv`**: una riga per `(visit_id, point, anchor_marker)`. Serie senza positivi = una riga con `no_cross_marker_effect=True` e campi àncora a None.
- **`cpm_ia_aggregated.csv`**: una riga per `point`, con `total_visit_count`, `positive_visit_count`, `positive_prevalence`, `median_positives_count`, mediane slope/depth/length/step per tutte le àncore del punto.
- Chiave di unicità G-09: `(visit_id, point, anchor_marker)`.

### Descent window closure rules (Rev 00.01)
La finestra di ciascuna àncora si chiude al **primo** tra:
1. `val - prev > epsilon` (innalzamento) → `window_close_reason = 'rise'`
2. Prossima àncora nella sequenza → `window_close_reason = 'next_positive'` (finestra chiusa **prima** del prossimo positivo)
3. `len(window) >= n_max` → `window_close_reason = 'n_max'`
4. Fine sequenza → `window_close_reason = 'end'`
NaN bridging invariato.

### Module execution order
config_loader → data_ingestion → marker_sequence → trigger_detection → positive_census → descent_window → descent_slope → descent_descriptors → variance_indicator → output_consolidation → report_generator

### Pipeline orchestration (main.py)
- **Input Excel multi-file:** il pipeline esegue un run completo (M02–M11) per ogni `<file>` configurato; gli output finiscono in `<output_path>/<visit_id>/`.
- **Batch resilience:** in modalità multi-file, gli errori per-visita (dataset vuoto, marker duplicati, ecc.) vengono catturati, loggati come WARNING, e il loop continua alle visite successive senza interrompere il run.
