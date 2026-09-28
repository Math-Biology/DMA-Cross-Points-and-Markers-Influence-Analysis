 

# 

# **Math B \- DMA \- Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications**

## 

## Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications

> **Rev 00.02 — review copy with change markup (Status: Draft — Design Review and approval pending).**
> Text added with respect to Rev 00.01 is shown as <ins>inserted text</ins>; removed text as <del>deleted text</del>. Unmarked text is unchanged from Rev 00.01 (the Rev 00.01 changes with respect to Rev 00.00 are accepted in this copy). The companion .docx carries the same changes as Word tracked changes (author: "Claude (AI-assisted, operator [IR])"); *Accept All Changes* yields the clean Rev 00.02.
>
> **Summary of changes (minor revision — design change during development, component not released, no DCR required):**
>
> 1. **SR extended to the consecutive-positive cluster behaviour implemented on 2026-09-28** (Design Input change, subject to Design Review): REQ-CPM-IA-P26.0004 (cluster membership per anchor and number of clustered positives per series; a missing value between two positives breaks adjacency) and REQ-CPM-IA-P26.0010 (new detail and aggregation fields).
> 2. **Technical Specifications**: new SPEC-CPM-IA-P26.0004.1 (Consecutive-Positive Cluster Detection, decimal-suffix rule, ref.3); SPEC-CPM-IA-P26.0010 and 0011 updated with the columns consecutive_run_length, consecutive_peaks and median_consecutive_peaks; Verification Method of SPEC-CPM-IA-P26.0010.1 updated to the renumbered cases TC-12-001 to TC-12-007.
> 3. **Risk Analysis**: new RISK-CPM-IA-P26.0004.1 (decimal suffix applied by analogy, as in Rev 00.01 — to be confirmed against the QMS); RISK-CPM-IA-P26.0010 mitigation extended.
> 4. **Verification Summary**: pytest evidence 2026-09-28 (223 passed, 0 failed) and open verification gaps on the cluster rule.
> 5. **Parameters**: adjacency rule added as a fixed design constant owned by SPEC-CPM-IA-P26.0004.1.
> 6. **Document information**: Effective Date and Current Revision. Applied procedures reconfirmed by the developer on 2026-09-28 (P26.0039, P26.0018, P26.0027 Rev 00.01). Doc ID still left unchanged (open finding: dedicated ID to be assigned from registry #L001-U001-P26.0004).


# 

# **TABLE OF CONTENTS**

[**1\. Document Information	3**](#document-information)

[2\. Definitions & Acronyms	3](#definitions-&-acronyms)

[3\. Referencies	3](#referencies)

[**4\. Introduction (Purpose & Scope)	5**](#introduction-\(purpose-&-scope\))

[**5\. Involved Components	5**](#involved-components)

[**6\. Specific Requirements	5**](#specific-requirements)

[**7\. Technical Specification	6**](#technical-specification)

[**8\. Risk Analysis	6**](#risk-analysis)

[**9. Verification Summary**](#verification-summary)

[**10\. Parameters	6**](#parameters)

[**11\. Document Governance	8**](#document-governance)

[11.1. Revision List & Notes	8](#revision-list-&-notes)

# 

1. # **Document Information** {#document-information}

| Doc. Title. | DMA \- Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications |
| :---- | :---- |
| Doc ID | \#PT-L01-U000-P26.xxxx |
| Doc Type | requirements & technical specification |
| Department  &/or Processes Area | R\&D |
| Effective Date | <del>24 September 2026</del><ins>28 September 2026</ins> |
| Current Revision | 00.<del>01</del><ins>02</ins> |
| Document Status | Draft — Design Review and approval pending |
| Short Doc Code | \[CPM-IA\] |

# 

2. # **Definitions & Acronyms**  {#definitions-&-acronyms}

| Def. / Acron. | Description |
| :---- | :---- |
|  Math B | Math Biology |
| DMA  | Deep Metabolic-process Assessment |
|  |  |
|  |  |
|  |  |

3. # **Referencies** {#referencies}

Unless otherwise specified, definitions and acronyms are defined in DOC-QMS-001 – Definitions, Acronyms & Ontology.

| Ref. | Doc ID | Description or Link |
| :---- | :---- | :---- |
| ref.1 | \#L001-U001-P26.0007 | Math B \- Definitions, Acronyms & Ontology |
| ref.2 | \#L001-U015-P26.0020 | Math B \- DMA \- Hardware & Software Components Tree & Accessory \- Registry |
| ref.3 | \#L001-U015-P26.0018 | Math B - Procedure - Protocols &amp; IDs Generation, Assignment &amp; Versioning, Rev 00.01 |
| ref.4 | \#L001-U015-P26.0039 | Math B - SOP - From Design To Test - Documentation - Principles, Rev 00.01 |
| ref.5 | \#L001-U015-P26.0035 | Math B \- DMA Screening \- General Hardware & Software Requirements |
| ref.6 | \#L001-U015-P26.0033 | Math B \- DMA Screening \- Design Traceability Matrix (DTM) \- MDR Class I |
| ref.7 | #L001-U015-P26.0027 | Math B - SOP - Product Design and Development Control, Rev 00.01 |

4. # **Introduction (Purpose & Scope)** {#introduction-(purpose-&-scope)}

This document defines the Cross Points and Markers Influence Analysis Specific Requirements (SR) and Technical Specifications (TS) for the DMA Screening system, a Class I medical device developed by Math Biology S.r.l. for the non-invasive acquisition of quasi-static bioelectrical surface currents. 

The document is produced in accordance with the Quality Management System requirements of ISO 13485:2016 and the applicable provisions of EU Regulation 2017/745 (MDR). It constitutes a formal design output record within the DMA Screening History File and provides the foundational input for the Design Traceability Matrix (DTM, ref.6). Requirements derivation, identifier coding, and traceability rules applied throughout this document follow the procedures defined in ref. 3 and ref. 4\.

Each specific requirement (SR) in this document is formally linked to a higher-level General Requirement (GR), establishing a clear vertical chain of compliance as required by ISO 13485:2016 Clause 7.3. Each SR is satisfied by one or more Technical Specifications (TS) in Section 7, each carrying a dedicated Verification Method, ensuring direct traceability for subsequent verification and validation activities (MDR Annex II, Section 3). SR and GR constitute the Design Inputs and TS the Design Outputs (ISO 13485:2016 Clauses 7.3.3 and 7.3.4).

## 

5. # **Involved Components** {#involved-components}

This document relates to the software components listed in the following table. For additional details about Components see **ref. 2\.**

**\[Select only the correct associated component, delete the others\]**

| Component\_ID | Versioning | Name |
| :---- | :---- | :---- |
|  |  |  |
|  |  |  |
|  |  |  |

6. # **Specific Requirements** {#specific-requirements}

This section lists all Specific Requirements for the Cross Points and Markers Influence Analysis. Each SR is derived from one or more General Requirements (GR) defined in **ref.5**. 

**\[REQ-CPM-IA-P26.0001\]**

Linked to: **\[REQ-G-P26.0072\]**

**External Configuration Loading**

Requirement: The component loads all execution parameters at runtime from an external XML configuration file, with no processing parameter hardcoded in the source. The configuration provides, as a minimum: the input source definition (source type and the related file paths or connection settings), the output path and the output-label suffixes; the positive-detection threshold (mandatory, currently set to 300 %); the rise tolerance ε used to close a descent window; the maximum number of descent points N_max; and the data-quality policy applied to non-conforming anatomical points. A missing or malformed configuration file, or a missing or invalid mandatory parameter, results in a controlled failure of the run.

**\[REQ-CPM-IA-P26.0002\]**

Linked to: **\[REQ-G-P26.0084\]**

**Autonomous Raw-Variation Ingestion**

Requirement: The component operates autonomously on the raw percentage-variation data produced by the Raw Variation Computation component, ingesting it from the configured source (a long-format CSV table, or per-visit Excel workbooks in wide layout, markers by anatomical points, whose visit identifier and visit date are supplied by the configuration) and normalising it into a long-format table in which every record identifies a visit, a marker and an anatomical point, together with its raw percentage variation and the associated visit metadata. The component validates the presence and type of the required fields, applies documented data-quality rules to records with empty keys or non-conforming anatomical-point names, and doesn't require input from any other running component to complete its computation.

**\[REQ-CPM-IA-P26.0003\]**

Linked to: **\[REQ-G-P26.0018\]**

**Marker Sequence Reconstruction**

Requirement: For each (visit, anatomical point) pair, the component reconstructs the ordered sequence of marker measurements that defines the analysis axis along which cross-marker influence is evaluated. The marker acquisition order must be derived deterministically, for each visit, from the order of first appearance of each marker within that visit's records, and applied consistently to every (visit, point) series of that visit, so that the notions of measurement “preceding” and “subsequent” to a given marker are unambiguously defined.

**\[REQ-CPM-IA-P26.0004\]**

Linked to: **\[REQ-G-P26.0018\]**

**All-Positive Trigger Detection**

Requirement: Within each (visit, point) marker sequence, the component detects every marker whose raw percentage variation is greater than or equal to the configured positive-detection threshold (currently 300 %) and designates each of them as a positive anchor (excitation onset), preserving their order in the marker sequence and reporting the number of positives of the series. Each anchor is the starting point of its own influence analysis. A series containing no marker reaching the threshold must be reported as having no cross-marker effect.<ins> The component also identifies clusters of consecutive positives, i.e. anchors located at adjacent positions of the marker sequence (sequence-index difference of one; a missing (NaN) value between two positives breaks adjacency), and reports, for each anchor, the length of the cluster it belongs to and, for each series, the number of anchors belonging to a cluster of at least two consecutive positives.</ins>

**\[REQ-CPM-IA-P26.0005\]**

Linked to: **\[REQ-G-P26.0018\]**

**Positive Census Across Points**

Requirement: The component determines, across all (visit, point) series processed in a run, how many and which anatomical points present at least one positive anchor, providing both the count and the identity of the positive points, together with the total number of anchors detected, as an explicit output. This census must enable quantification of the prevalence of the cross-marker excitation phenomenon at anatomical-point level within the scope of the run.

**\[REQ-CPM-IA-P26.0006\]**

Linked to: **\[REQ-G-P26.0018\]**

**Adaptive Descent-Window Determination**

Requirement: Starting from each positive anchor of a (visit, point) series, the component determines the influence (descent) window as the anchor followed by the maximal run of non-increasing consecutive marker measurements. The window must be closed at the first of: (i) the first significant rise, defined as a consecutive increase exceeding the configured rise tolerance ε; (ii) the next positive anchor of the same series, which is excluded from the window; (iii) the maximum length of N_max points; (iv) the end of the sequence. The reason for closing the window must be recorded, and missing measurements must be skipped without closing the window. The number of points retained must therefore be adaptive to the actual length of the descent.

**\[REQ-CPM-IA-P26.0007\]**

Linked to: **\[REQ-G-P26.0018\]**

**Descent Slope Computation**

Requirement: For each positive anchor with an identified descent window, the component computes the slope (rate of decrease) of the descending curve over that window, treating the marker positions as equally spaced abscissae. The slope must be obtained by the standard least-squares linear-regression estimate over the window’s points, so that the resulting value expresses the average percentage-point change per marker step; for a minimal window of two points this estimate coincides with the elementary secant slope.

**\[REQ-CPM-IA-P26.0008\]**

Linked to: **\[REQ-G-P26.0018\]**

**Descent Shape Descriptors**

Requirement: In addition to the slope, the component computes, for each positive anchor, descriptors characterising the descending curve that follows it, comprising, as a minimum: the descent depth (difference between the anchor value and the minimum value within the window), the descent length (number of points in the window), and the mean per-step decrease. These descriptors must quantify the magnitude and the extent of the excitation decay.

**\[REQ-CPM-IA-P26.0009\]**

Linked to: **\[REQ-G-P26.0018\]**

**Pre/Post Positive Variance Indicator**

Requirement: For each positive anchor of a (visit, point) series, the component computes a dispersion indicator of the marker measurements before and after that anchor, where the “before” segment comprises all the markers preceding the anchor in the sequence (including any earlier anchors and their descent windows, missing values excluded) and the “after” segment comprises the markers within that anchor's descent window. The indicator must be expressed as the statistical variance of each segment, enabling comparison of measurement dispersion prior to and following the excitation. The component additionally reports the normalised variance_ratio = variance_after / variance_before as a comparative dispersion indicator, which is undefined (None) when either variance cannot be computed or the pre-anchor variance is zero.

**\[REQ-CPM-IA-P26.0010\]**

Linked to: **\[REQ-G-P26.0031\]**

**Consolidated Tidy Output and Per-Point Aggregation**

Requirement: The component consolidates its results into tidy (long-format) outputs at two levels: a per-(visit, point, anchor) record carrying the anchor identity, rank and value, the number of positives of the series, <ins>the length of the anchor’s consecutive-positive cluster and the number of clustered positives of the series, </ins>the descent-window characteristics (slope, depth, length, mean per-step decrease, closing reason) and the pre/post variance indicators, with a single record flagged as having no cross-marker effect for each series without positives; and a per-point aggregation summarising the prevalence of positive visits, the median number of positives per series<ins>, the median number of clustered positives over the positive series of the point</ins> and the central tendency (median over all anchors of the point) of the descent metrics. Each output record must be uniquely identified by its grouping keys together with the relevant visit metadata, and existing outputs must never be overwritten. When the input is a set of per-visit Excel workbooks, each visit is processed and written independently to its own output folder, and a failure on one visit must be logged and must not prevent the processing of the remaining visits.

**\[REQ-CPM-IA-P26.0011\]**

Linked to: **\[REQ-G-P26.0022\], \[REQ-G-P26.0028\], \[REQ-G-P26.0029\]**

**Automated Run Report Generation [OBSOLETE]**

Requirement: [Status: Obsolete since Rev 00.01. The PDF report module (M11) was removed from the implementation on 2026-09-24; this SR has no active Technical Specification, is excluded from the DTM and is retained only for DHF traceability.] The component shall generate a formatted PDF run report summarising the analysis results — run parameters, series- and point-level positivity statistics, per-point prevalence and descent medians, and an anchor-marker summary — assembled through a programmatic templating engine (LaTeX / pdflatex) that enforces a fixed, auditable layout. Report generation shall fail in a controlled manner and shall not overwrite an existing report. All report text shall use non-diagnostic language. 

7. # **Technical Specification** {#technical-specification}

This section provides the Technical Specification for each Specific Requirement defined in Section 6\. 

**\[SPEC-CPM-IA-P26.0001\]**

Linked to: **\[REQ-CPM-IA-P26.0001\]**

**External Configuration Loading**

Specification: config_loader.load_config() parses the XML configuration via xml.etree.ElementTree into an immutable (frozen) CpmIaConfig dataclass. The input source is read from the &lt;input&gt; block: &lt;type&gt; (csv \| excel \| db), &lt;csv&gt;&lt;path&gt;, the list of &lt;excel&gt;&lt;file&gt; entries each carrying &lt;path&gt;, &lt;visit_id&gt; and &lt;visit_date&gt;, and &lt;db&gt;&lt;dsn_env&gt;/&lt;query&gt;; a legacy &lt;input_path&gt; element is accepted as a CSV source when no &lt;input&gt; block is present. Required elements: output_path, output_label_detail, output_label_aggregated, threshold_pct (float), rise_tolerance_epsilon (float) and n_max (int); threshold_pct has no default. A missing file, malformed XML, a missing or blank required element, an Excel &lt;file&gt; lacking one of its three sub-elements, or an uncastable value raises ConfigurationError, aborting the run before any processing. No processing parameter is hardcoded in the source.

Verification Method: Automated unit test tests/test_config_loader.py, cases TC-01-001 to TC-01-011 and TC-01-013 (valid csv and excel load, immutability, legacy input_path, missing file, malformed or empty XML, missing or non-integer n_max, missing epsilon, malformed and absent threshold_pct, blank output label, missing input block, input description).

**[SPEC-CPM-IA-P26.0001.1]**

Linked to: **[REQ-CPM-IA-P26.0001]**

**Data-Quality Configuration**

Specification: The optional &lt;data_quality&gt;&lt;drop_invalid_points&gt; element is parsed into DataQualityConfig.drop_invalid_points: the values 'true', '1' or 'yes' (case-insensitive) enable the drop policy, any other non-blank value disables it, and an absent block or a blank element defaults to True. The flag is consumed by data_ingestion.load_data() (SPEC-CPM-IA-P26.0002.2).

Verification Method: Automated unit test tests/test_config_loader.py, case TC-01-012 (drop true, drop false, absent block defaults to true).


**\[SPEC-CPM-IA-P26.0002\]**

Linked to: **\[REQ-CPM-IA-P26.0002\]**

**Autonomous Raw-Variation Ingestion**

Specification: data_ingestion.load_data() dispatches on config.input.type to a DataSource implementation: CsvSource (UTF-8 CSV; a missing file or a suffix other than .csv raises IngestionError), ExcelSource (SPEC-CPM-IA-P26.0002.1) or PostgresSource. PostgresSource is a reserved stub that always raises IngestionError, so database ingestion is not available in this version. An unknown type, or a type whose configuration block is missing, raises IngestionError. The long-format table must contain the columns visit_id, marker, point, percentage_variation and visit_date (missing column: IngestionError). percentage_variation is coerced to float64: genuine empty values are preserved as NaN (missing measurement) while non-numeric text raises IngestionError; a NaN in any key column (visit_id, marker, point) raises IngestionError; visit_date is kept as text. The function returns the validated table together with a DataQualityReport (SPEC-CPM-IA-P26.0002.2) and completes without input from any other running component.

Verification Method: Automated unit test tests/test_data_ingestion.py, cases TC-02-001 to TC-02-007 and TC-02-009 (valid CSV, missing column, NA string versus text value, NaN key, missing file, wrong suffix, header-only file, Postgres stub rejection).

**[SPEC-CPM-IA-P26.0002.1]**

Linked to: **[REQ-CPM-IA-P26.0002]**

**Excel Wide-Format Ingestion**

Specification: ExcelSource.load() opens each configured workbook with openpyxl (data_only=True, active sheet); a missing openpyxl package or a missing file raises IngestionError. Row 1 is the header: column A holds the marker and every following non-empty header cell is an anatomical point (empty headers are skipped). Each data row with a non-empty marker is melted into one long-format record per point, with visit_id and visit_date taken from the corresponding &lt;file&gt; entry of the configuration. The records of all configured files are concatenated; when no record is produced an empty table with the required columns is returned.

Verification Method: Automated unit test tests/test_data_ingestion.py, case TC-02-008 (Excel dispatch, null header skipping, multi-file concatenation).

**[SPEC-CPM-IA-P26.0002.2]**

Linked to: **[REQ-CPM-IA-P26.0002]**

**Input Data-Quality Rules**

Specification: After type validation, load_data() drops every record whose visit_id, marker or point is empty or whitespace-only (WARNING logged). It then validates each anatomical-point name against the pattern ^[LR][HF]\s*-\s*\d+\s*-\s*\S+(\s*-\s*.+)?\|.+\s*\[\d+\]\s*$, which accepts the four-component format (e.g. 'LH - 2 - i - colon'), the three-component format (e.g. 'LH - 3 - c') and the legacy format (e.g. 'SomeName [3]'). Records with a non-conforming point name are dropped with a WARNING listing the invalid names when drop_invalid_points is True, or kept with a WARNING when it is False. The counts and the invalid names are returned in an immutable DataQualityReport (total_rows, rows_dropped_empty_keys, invalid_point_names, rows_affected_invalid_points, drop_mode). The orchestrator does not persist the DataQualityReport: the run log is the only persistent evidence of the excluded records.

Verification Method: Automated unit test tests/test_data_ingestion.py, cases TC-02-001 (report fields), TC-02-010 (invalid point dropped or kept) and TC-02-011 (three-component valid, two-component invalid, four-component valid).


**\[SPEC-CPM-IA-P26.0003\]**

Linked to: **\[REQ-CPM-IA-P26.0003\]**

**Marker Sequence Reconstruction**

Specification: marker_sequence.build_sequences() first removes exact duplicate rows (same visit_id, marker, point and percentage_variation, NaN treated as equal) with a WARNING. It then derives, for each visit, the marker order as the order of first appearance within that visit's rows (dict.fromkeys over a groupby with sort=False — never sorted(), set() or unique()), and builds per-(visit, point) value sequences aligned to that visit's order, filling markers absent for the point with float('nan'). A remaining repeated (visit, point, marker) triplet with different values raises SequenceError, as does an empty input dataset.

Verification Method: Automated unit test tests/test_marker_sequence.py, cases TC-03-001 to TC-03-009 (first-appearance order, non-alphabetical order, NaN fill, conflicting triplet, empty input, single row, consistent index-to-marker mapping, exact-duplicate removal, NaN-versus-value conflict).

**\[SPEC-CPM-IA-P26.0004\]**

Linked to: **\[REQ-CPM-IA-P26.0004\]**

**All-Positive Trigger Detection**

Specification: trigger_detection.detect_triggers() scans each (visit, point) sequence in per-visit order and records as an immutable Anchor (marker, index, value) every non-NaN value greater than or equal to threshold_pct (inclusive comparison), in sequence order. Each series yields an immutable TriggerResult with anchors (ordered list), positives_count = len(anchors) and no_cross_marker_effect = True when no anchor is found. NaN positions are skipped. An empty sequence set returns an empty result; threshold_pct &lt;= 0 raises TriggerError.

Verification Method: Automated unit test tests/test_trigger_detection.py, cases TC-04-001 to TC-04-013 (first positive, no positive, all positives collected in order, all-NaN series, zero and negative threshold, exact-threshold inclusion, NaN skipping, empty input, mixed series, immutability, anchor fields).

**<ins>[SPEC-CPM-IA-P26.0004.1]</ins>**

<ins>Linked to: **[REQ-CPM-IA-P26.0004]**</ins>

**<ins>Consecutive-Positive Cluster Detection</ins>**

<ins>Specification: trigger_detection._compute_consecutive_runs(), invoked by TriggerResult.__post_init__ for every (visit, point) series, partitions the ordered anchor list into maximal runs in which anchors[k+1].index == anchors[k].index + 1. The comparison uses the per-visit sequence index with NaN positions included, so a NaN value between two positives breaks the run. It sets anchor_run_lengths, a list aligned one-to-one with anchors holding the length of the run each anchor belongs to (1 for an isolated anchor, empty list when the series has no anchor), and consecutive_peaks, the number of anchors belonging to a run of length >= 2 (0 when all anchors are isolated or the series has no anchor). Both fields are computed once at construction and are immutable (frozen dataclass). Examples: anchors at indices 0, 1, 3, 4 give anchor_run_lengths = [2, 2, 2, 2] and consecutive_peaks = 4; anchors at 0, 1, 3 give [2, 2, 1] and 2. The adjacency rule (index + 1) is a fixed design constant and is not configurable.</ins>

<ins>Verification Method: Automated unit test tests/test_trigger_detection.py, case TC-04-014 (seven test functions: no anchors, single isolated anchor, two and three consecutive anchors, non-consecutive anchors, leading and trailing consecutive pair).</ins>

**\[SPEC-CPM-IA-P26.0005\]**

Linked to: **\[REQ-CPM-IA-P26.0005\]**

**Positive Census Across Points**

Specification: positive_census.compute_census() aggregates the trigger results to anatomical-point level, returning an immutable PointCensus with positive_point_count, a lexicographically sorted positive_points list, total_point_count (unique points) and total_positives_count (sum of positives_count over all series). A point is positive when at least one (visit, point) series has no_cross_marker_effect = False. Empty input returns a zero census. The census is logged at INFO level and cross-checked against the per-point aggregation (SPEC-CPM-IA-P26.0011), a divergence being logged as WARNING.

Verification Method: Automated unit test tests/test_positive_census.py, cases TC-05-001 to TC-05-009 (count and identity, no positives, single pair, empty input, mixed visits, deterministic sorting, unique counting, immutability, total_positives_count).

**\[SPEC-CPM-IA-P26.0006\]**

Linked to: **\[REQ-CPM-IA-P26.0006\]**

**Adaptive Descent-Window Determination**

Specification: descent_window.determine_descent_windows() builds one immutable DescentWindow per anchor, starting with the anchor value. Subsequent values are scanned in order: NaN values are bridged (skipped, the last valid value being retained as reference); the window is closed, without including the current value, at the first of (1) the position of the next anchor of the same series (window_close_reason = 'next_positive'), (2) a rise where (val - prev) &gt; rise_tolerance_epsilon ('rise'), (3) a window already holding n_max values ('n_max', truncated_by_n_max = True); otherwise it closes at the end of the sequence ('end'). The checks are applied in the order listed. Series with no anchor map to an empty list. n_max &lt; 1, rise_tolerance_epsilon &lt; 0 or an out-of-bounds anchor index raise DescentError.

Verification Method: Automated unit test tests/test_descent_window.py, cases TC-06-001 to TC-06-014 (close on rise, epsilon boundary, n_max truncation, single-point windows, no-effect series, invalid parameters, NaN bridging, epsilon = 0, n_max = 1, multiple pairs, two and adjacent anchors closed at next_positive, window_close_reason presence).

**\[SPEC-CPM-IA-P26.0007\]**

Linked to: **\[REQ-CPM-IA-P26.0007\]**

**Descent Slope Computation**

Specification: descent_slope.compute_slopes() computes, for the descent window of each anchor, the ordinary-least-squares slope with equally spaced abscissae x = 0..L-1 using the closed form slope = (n*Sum(i*yi) - Sum(i)*Sum(yi)) / (n*Sum(i^2) - (Sum(i))^2), returning per (visit, point) a list of slopes aligned with the anchor list. Single-point windows return None (WARNING logged); a NaN inside a window raises SlopeError. For a two-point window the estimate coincides with the elementary secant slope.

Verification Method: Automated unit test tests/test_descent_slope.py, cases TC-07-001 to TC-07-010, including numerical cross-validation of the closed form against numpy.polyfit and multi-anchor slope lists.

**\[SPEC-CPM-IA-P26.0008\]**

Linked to: **\[REQ-CPM-IA-P26.0008\]**

**Descent Shape Descriptors**

Specification: descent_descriptors.compute_descriptors() returns, for the window of each anchor, an immutable DescentDescriptor with descent_depth = anchor_value - min(window_values), descent_length = number of points in the window, and mean_per_step_decrease = depth / (length - 1) (0.0 when length == 1), the anchor value being taken from the corresponding Anchor of the trigger results. Series without anchors map to an empty list; a NaN in the window raises DescriptorError.

Verification Method: Automated unit test tests/test_descent_descriptors.py, cases TC-08-001 to TC-08-009 (depth, length, mean per step, single-point case, no-effect series, NaN error, global minimum, two-point window, mixed pairs, multi-anchor lists).

**\[SPEC-CPM-IA-P26.0009\]**

Linked to: **\[REQ-CPM-IA-P26.0009\]**

**Pre/Post Positive Variance Indicator**

Specification: variance_indicator.compute_variance_indicators() computes, for each anchor, the sample variance (statistics.variance, ddof = 1) of the pre-anchor segment (all sequence values at positions preceding the anchor index, NaN removed) and of the post-anchor segment (that anchor's descent-window values, NaN removed), and variance_ratio = variance_after / variance_before. Each variance is None when its cleaned segment holds fewer than two points; variance_ratio is None when either variance is None or variance_before is not greater than 0. Series with no_cross_marker_effect = True map to an empty list.

Verification Method: Automated unit test tests/test_variance_indicator.py, cases TC-09-001 to TC-09-011, including TC-09-010 (variance_ratio) and TC-09-011 (one indicator per anchor).

**\[SPEC-CPM-IA-P26.0010\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Consolidated Tidy Detail Output**

Specification: output_consolidation._build_detail() emits one tidy (long-format) row per (visit, point, anchor), with the analytical columns in fixed order: anchor_rank (1-based), anchor_marker, anchor_value, anchor_index, positives_count, <ins>consecutive_run_length, consecutive_peaks, </ins>no_cross_marker_effect, descent_slope, descent_depth, descent_length, mean_per_step_decrease, window_close_reason, variance_before, variance_after, variance_ratio. A series without positives yields a single row with no_cross_marker_effect = True, positives_count = 0<ins>, consecutive_peaks = 0</ins> and empty anchor<ins>, cluster-length</ins> and metric fields.<ins> consecutive_run_length and consecutive_peaks are taken from the trigger result of the series (SPEC-CPM-IA-P26.0004.1); consecutive_peaks is repeated on every anchor row of the series.</ins> Visit metadata (all input columns except marker and percentage_variation) is left-joined on (visit_id, point); a missing metadata row or a duplicate (visit_id, point, anchor_marker) key raises OutputError. The table is written to {output_path}/{output_label_detail}.csv (UTF-8, no index); the output directory is created if absent and a pre-existing file raises OutputError (no overwrite, G-10).

Verification Method: Automated unit test tests/test_output_consolidation.py, cases TC-10-001, TC-10-002, TC-10-003, TC-10-005, TC-10-006, TC-10-008, TC-10-009<del> and</del><ins>,</ins> TC-10-010<ins> and TC-10-011</ins> (row counts, no-effect row, no-overwrite guard, metadata conflict, directory creation, column schema, multi-anchor rows, key uniqueness<ins>, consecutive-cluster columns</ins>).

**[SPEC-CPM-IA-P26.0010.1]**

Linked to: **[REQ-CPM-IA-P26.0010]**

**Per-Visit Orchestration and Batch Resilience**

Specification: main.run_pipeline() loads the configuration (M01) and executes modules M02 to M10 in the documented order. When the input type is excel and more than one &lt;file&gt; is configured, each file is processed as an independent run with a configuration restricted to that file and output_path set to {output_path}/{visit_id}, so that census and per-point aggregation refer to a single visit. Any exception raised while processing a visit is caught, logged as WARNING with the visit identifier and the exception type, and the loop continues with the next visit; a final INFO line reports the processed and skipped visits, and the tables of the last successful visit are returned. In single-input mode every typed exception propagates. main() exits with code 0 on completion and with code 1 on a missing argument or on any propagated exception.

Verification Method: Automated unit test tests/test_main.py, cases TC-1<del>1</del><ins>2</ins>-001 to TC-1<del>1</del><ins>2</ins>-007 (end-to-end run, missing config, CSV outputs, exit codes, per-visit output subfolders, empty visit skipped while the valid visit is processed).<del> Note: these case IDs reuse the numbering of the Rev 00.00 report-generator tests.</del>


**\[SPEC-CPM-IA-P26.0011\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Per-Point Aggregation Output**

Specification: output_consolidation._build_aggregation() emits one row per point with total_visit_count (distinct visits), positive_visit_count (distinct visits with at least one anchor), median_positives_count (median of positives_count over the positive (visit, point) series), <ins>median_consecutive_peaks (median of consecutive_peaks over the positive (visit, point) series of the point), </ins>median_descent_slope, median_descent_depth, median_descent_length and median_mean_per_step_decrease (medians over all anchor rows of the point), and positive_prevalence = positive_visit_count / total_visit_count. An internal census cross-check logs a WARNING on divergence. The file is written to {output_path}/{output_label_aggregated}.csv under the same no-overwrite rule as SPEC-CPM-IA-P26.0010.

Verification Method: Automated unit test tests/test_output_consolidation.py, cases TC-10-001, TC-10-003, TC-10-004, TC-10-007<del> and</del><ins>,</ins> TC-10-008<ins> and TC-10-011</ins> (aggregation row count, no-overwrite guard, medians and prevalence, all no-effect case, column schema<ins>, median of clustered positives</ins>).

**\[SPEC-CPM-IA-P26.0012\]**

Linked to: **\[REQ-CPM-IA-P26.0011\]**

**Automated PDF Run Report [OBSOLETE]**

[Status: Obsolete since Rev 00.01. report_generator.py, the LaTeX template and tests/test_report_generator.py were removed on 2026-09-24; this TS describes no active code, is excluded from the DTM and is retained only for DHF traceability.] Specification: report_generator.generate_report() fills the LaTeX template data/templates/cpm_ia_report.tex.template with run statistics and per-point tables, escaping LaTeX special characters and stripping C1 control characters, then compiles the source to PDF with two pdflatex passes (correct table-of-contents page numbers). The .tex source is always written and preserved on failure; a missing template, an absent pdflatex, a compilation failure, or a pre-existing PDF raises ReportError. The anchor-summary table applies a fixed presentation threshold of 3.5 % (rows with anchor_pct &gt;= 3.5). NOTE: this 3.5 % constant is currently hardcoded in report_generator.py and is recorded in the Parameters chapter as a fixed presentation constant.

Verification Method: Not applicable since Rev 00.01 (implementation and test file tests/test_report_generator.py removed). Historical evidence: cases TC-11-001 to TC-11-018 of Rev 00.00.

8. # **Risk Analysis** {#risk-analysis}

This section provides the Risk Analysis entries for each Specific Requirement, in compliance with ISO 14971 and ref.4. For each risk, severity × probability establishes the initial risk level; the mitigation link identifies the SR/TS providing the control; residual risk is stated after mitigation.

**\[RISK-CPM-IA-P26.0001\]**

Linked to: **\[REQ-CPM-IA-P26.0001\]**

**Execution with unintended parameters**

Risk: Hazard: the analysis runs on wrong thresholds because a malformed or partial configuration is accepted, producing a misleading non-clinical indication. Cause: silent acceptance of an invalid config or silent use of a default threshold. Initial risk: Severity 3 x Probability 2 = Medium. Mitigation: fail-closed validation of every required field, threshold_pct included (no default), with a controlled ConfigurationError abort (SPEC-CPM-IA-P26.0001, SPEC-CPM-IA-P26.0001.1). Residual risk: Low.

**\[RISK-CPM-IA-P26.0002\]**

Linked to: **\[REQ-CPM-IA-P26.0002\]**

**Corrupted or mistyped input data admitted**

Risk: Hazard: non-numeric or key-missing records enter the computation, corrupting downstream metrics. Cause: absent schema validation, or wrong melting of Excel wide workbooks. Initial risk: Severity 3 x Probability 2 = Medium. Mitigation: mandatory schema and type validation after every source, IngestionError on any violation, and deterministic header-driven melting of Excel workbooks (SPEC-CPM-IA-P26.0002, SPEC-CPM-IA-P26.0002.1). Residual risk: Low.

**[RISK-CPM-IA-P26.0002.1]**

Linked to: **[REQ-CPM-IA-P26.0002]; [SPEC-CPM-IA-P26.0002.2]**

**Silent exclusion of input records**

Risk: Hazard: valid measurements are excluded because their anatomical-point names do not match the accepted patterns, and the exclusion is not traceable in the outputs, biasing prevalence and descent statistics. Cause: point-naming variants not covered by the pattern; DataQualityReport not persisted by the orchestrator. Initial risk: Severity 3 x Probability 3 = Medium. Mitigation: configurable drop policy (drop_invalid_points), WARNING log listing every invalid point name and the number of affected rows, pattern and policy documented as fixed parameters (SPEC-CPM-IA-P26.0001.1, SPEC-CPM-IA-P26.0002.2). Residual risk: Medium — open action: persist the DataQualityReport alongside the run outputs.


**\[RISK-CPM-IA-P26.0003\]**

Linked to: **\[REQ-CPM-IA-P26.0003\]**

**Marker order corrupted**

Risk: Hazard: the notions of preceding and subsequent marker are inverted, so cross-marker influence is attributed to the wrong marker. Cause: reordering the sequence by sorting instead of first-appearance order. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: deterministic first-appearance ordering per visit, explicitly forbidding sort/set/unique, unit-tested for immutability (SPEC-CPM-IA-P26.0003). Residual risk: Low.

**\[RISK-CPM-IA-P26.0004\]**

Linked to: **\[REQ-CPM-IA-P26.0004\]**

**Incorrect excitation anchoring**

Risk: Hazard: a positive is missed or spuriously added, or the anchors are mis-ordered, shifting the influence analysis and producing a misleading indication. Cause: wrong threshold comparison (e.g. a value equal to the threshold misclassified), NaN mishandling or loss of sequence order. Initial risk: Severity 3 x Probability 2 = Medium. Mitigation: inclusive &gt;= comparison unit-tested at the exact threshold, NaN skipping, ordered anchor list with positives_count consistency and explicit no-effect flagging (SPEC-CPM-IA-P26.0004). Residual risk: Low.

**<ins>[RISK-CPM-IA-P26.0004.1]</ins>**

<ins>Linked to: **[REQ-CPM-IA-P26.0004]; [SPEC-CPM-IA-P26.0004.1]**</ins>

**<ins>Misreported consecutive-positive clusters</ins>**

<ins>Risk: Hazard: cluster membership or the number of clustered positives is computed incorrectly, or consecutive_peaks / median_consecutive_peaks is read as a maximum run length, misrepresenting clustered excitation in the output. Cause: wrong adjacency rule or NaN treatment; residual "maximum" wording in code comments and test docstrings; the term "peaks" differs from the "positive / anchor" terminology. Initial risk: Severity 2 x Probability 3 = Medium. Mitigation: fixed index + 1 adjacency rule with NaN breaking the run, fields computed once at construction and immutable, count semantics defined in REQ-CPM-IA-P26.0004 and SPEC-CPM-IA-P26.0004.1 and carried unchanged to the outputs (SPEC-CPM-IA-P26.0010, SPEC-CPM-IA-P26.0011), unit-tested by TC-04-014 and TC-10-011. Residual risk: Medium — open actions: add test cases for a NaN between two positives and for two separate clusters in one series; align the "maximum" wording in code and tests with the specified semantics.</ins>


**\[RISK-CPM-IA-P26.0005\]**

Linked to: **\[REQ-CPM-IA-P26.0005\]**

**Misstated prevalence of the phenomenon**

Risk: Hazard: the count or identity of positive anatomical points is wrong, misrepresenting how widespread the cross-marker effect is. Cause: duplicate or missed points in aggregation. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: set-based unique counting with deterministic sorted output, cross-checked against the aggregation table (SPEC-CPM-IA-P26.0005). Residual risk: Low.

**\[RISK-CPM-IA-P26.0006\]**

Linked to: **\[REQ-CPM-IA-P26.0006\]**

**Descent window mis-delimited**

Risk: Hazard: the influence window is too long or too short, or the windows of consecutive anchors overlap, distorting every descent metric derived from them. Cause: wrong rise-tolerance handling, missing length cap or missing boundary at the next anchor. Initial risk: Severity 3 x Probability 2 = Medium. Mitigation: epsilon-based closure at the first significant rise, closure before the next anchor, a hard n_max cap with truncation flagging, and a recorded window_close_reason, unit-tested (SPEC-CPM-IA-P26.0006). Residual risk: Low.

**\[RISK-CPM-IA-P26.0007\]**

Linked to: **\[REQ-CPM-IA-P26.0007\]**

**Incorrect slope estimate**

Risk: Hazard: the descent rate is computed incorrectly, misrepresenting the decay of the excitation. Cause: an unverified regression implementation. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: closed-form OLS cross-validated against numpy.polyfit, with None returned for undefined single-point windows (SPEC-CPM-IA-P26.0007). Residual risk: Low.

**\[RISK-CPM-IA-P26.0008\]**

Linked to: **\[REQ-CPM-IA-P26.0008\]**

**Misleading shape descriptors**

Risk: Hazard: depth, length or mean-per-step values misstate the magnitude and extent of the decay. Cause: arithmetic or boundary errors. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: explicit formulas with the length \== 1 boundary handled and NaN guarded, unit-tested (SPEC-CPM-IA-P26.0008). Residual risk: Low.

**\[RISK-CPM-IA-P26.0009\]**

Linked to: **\[REQ-CPM-IA-P26.0009\]**

**Invalid dispersion comparison**

Risk: Hazard: the pre/post variance comparison is undefined or misleading when a segment is too short or invariant, or when the pre-anchor segment includes earlier anchors and their descents. Cause: variance computed on fewer than two points, division by a zero baseline, or misreading of the documented pre-anchor segment definition. Initial risk: Severity 2 x Probability 2 = Low. Mitigation: sample variance guarded to require at least two points, variance_ratio suppressed (None) when the pre-anchor variance is zero, and the pre-anchor segment definition stated explicitly in REQ-CPM-IA-P26.0009 (SPEC-CPM-IA-P26.0009). Residual risk: Low.

**\[RISK-CPM-IA-P26.0010\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Output ambiguity or silent overwrite**

Risk: Hazard: results are not uniquely identifiable or a prior run's output is silently destroyed, breaking traceability. Cause: duplicate keys after join or overwriting existing files. Initial risk: Severity 3 x Probability 2 = Medium. Mitigation: enforced (visit_id, point, anchor_marker) uniqueness and a no-overwrite guard, both raising OutputError<ins>, and a fixed, schema-tested column set including the consecutive-cluster fields</ins> (SPEC-CPM-IA-P26.0010, SPEC-CPM-IA-P26.0011). Residual risk: Low.

**[RISK-CPM-IA-P26.0010.1]**

Linked to: **[REQ-CPM-IA-P26.0010]; [SPEC-CPM-IA-P26.0010.1]**

**Masked batch failures and misread per-visit statistics**

Risk: Hazard: in multi-file mode failing visits are skipped while the process still exits with code 0, and the per-visit prevalence (always 0 or 1) may be misread as a cross-visit prevalence. Cause: batch-resilience design catching every per-visit exception; per-visit output scope. Initial risk: Severity 3 x Probability 3 = Medium. Mitigation: WARNING per skipped visit with the exception type, final processed/skipped summary, per-visit output folders, single-visit scope documented in REQ-CPM-IA-P26.0010 and SPEC-CPM-IA-P26.0010.1. Residual risk: Medium — open actions: skipped-visit manifest or non-zero exit code when visits are skipped; cross-visit aggregation if prevalence across visits is required.


**\[RISK-CPM-IA-P26.0011\]**

Linked to: **\[REQ-CPM-IA-P26.0011\]**

**Non-compliant or corrupted report output [OBSOLETE]**

[Status: Obsolete since Rev 00.01, together with REQ-CPM-IA-P26.0011 and SPEC-CPM-IA-P26.0012.] Risk: Hazard: the run report is malformed, silently overwrites a prior report, or renders unescaped content, undermining the auditability of the output. Cause: template/compilation failure or missing collision guard. Initial risk: Severity 2 x Probability 2 = Low. Mitigation: LaTeX escaping, controlled ReportError on template/pdflatex failure, and a no-overwrite guard; non-diagnostic language per REQ-G-P26.0022/0028 applies to all report text (SPEC-CPM-IA-P26.0012). Residual risk: Low.

9. # **Verification Summary** {#verification-summary}

This section records the verification evidence available for this revision (ref.4, ref.7).

Activity type: Design Verification (software unit testing). Automated test suite executed on 2026-09-2<del>4</del><ins>8</ins> against the Rev 00.0<del>1</del><ins>2</ins> source code (Python 3.10.12, pytest, developer workstation): <del>211 test cases collected, 211 passed</del><ins>223 test cases collected, 223 passed</ins>, 0 failed. Test files: tests/test_config_loader.py, test_data_ingestion.py, test_marker_sequence.py, test_trigger_detection.py, test_positive_census.py, test_descent_window.py, test_descent_slope.py, test_descent_descriptors.py, test_variance_indicator.py, test_output_consolidation.py, test_main.py.

[Placeholder — the formal Test Report (ID format TRCPM-IA-dddd, template #L001-U001-P26.0143) is to be issued by Math Biology S.r.l. upon completion of the independent verification activity, and its ID linked to every TS on the DTM.]

Interface clause (ref.7): all current test cases use synthetic fixtures. Verification of the component on the actual output of the Raw Variation Computation component (connected/interfaced condition) is pending.

<ins>Open verification gaps on SPEC-CPM-IA-P26.0004.1 (RISK-CPM-IA-P26.0004.1): no test case covers a NaN value between two positives (adjacency broken) or a series with two separate clusters (where the count semantics, e.g. 4, differs from a maximum run length, e.g. 2). The test docstrings of TC-04-014 and TC-10-011 and a code comment in output_consolidation._build_aggregation() still describe a "maximum" run length and must be aligned with the specified count semantics.</ins>

10. # **Parameters** {#parameters}

This section contains the fixed parameters for the documented component version (source code Rev 00.0<del>1</del><ins>2</ins>, versioned XML configuration data/config/cpm_ia_config.xml) of the Cross Points and Markers Influence Analysis.

| Parameter | Value | Description |
| :---- | :---- | :---- |
| threshold\_pct | 300.0 | Positive-detection threshold (%). Mandatory configuration element; a marker is positive when value &gt;= threshold. SPEC-CPM-IA-P26.0001 / 0004. |
| rise_tolerance_epsilon | 1.0 | Maximum consecutive increase (percentage points) tolerated before a descent window closes. SPEC-CPM-IA-P26.0001 / 0006. Value to be calibrated. |
| n\_max | 1000 | Maximum descent-window length (points). SPEC-CPM-IA-P26.0001 / 0006. Value to be calibrated; at 1000 the cap is not reached by the current marker panels. |
|  |  |  |
| drop_invalid_points | true | Records with non-conforming anatomical-point names are dropped (WARNING logged). SPEC-CPM-IA-P26.0001.1 / 0002.2. |
| Input source type | excel | Value in the versioned default configuration; supported: csv, excel; db reserved (not implemented). SPEC-CPM-IA-P26.0001 / 0002 / 0002.1. |
| Required input columns | visit_id, marker, point, percentage_variation, visit_date | Long-format schema after normalisation; percentage_variation as float64. SPEC-CPM-IA-P26.0002. |
| Anatomical-point pattern | ^[LR][HF]\s*-\s*\d+\s*-\s*\S+(\s*-\s*.+)?\|.+\s*\[\d+\]\s*$ | Accepted point-name formats: 4-component, 3-component and legacy 'Name [n]'. SPEC-CPM-IA-P26.0002.2. |
| Output labels | cpm_ia_detail / cpm_ia_aggregated | Detail and aggregation CSV names; per-visit subfolder {output_path}/{visit_id} in Excel multi-file mode. SPEC-CPM-IA-P26.0010 / 0011 / 0010.1. |
| Detail uniqueness key | (visit_id, point, anchor_marker) | G-09 key of the detail output. SPEC-CPM-IA-P26.0010. |
| <ins>Consecutive-positive adjacency</ins> | <ins>index + 1 (NaN breaks adjacency)</ins> | <ins>Fixed design constant, not configurable: two anchors belong to the same cluster when their per-visit sequence indices differ by one. SPEC-CPM-IA-P26.0004.1.</ins> |

# 

# 

11. # **Document Governance** {#document-governance}

    1. ## **Revision List & Notes**  {#revision-list-&-notes}

| Revisision  | Date | Approved By \-  Name Acronymus | Notes |
| :---- | :---- | :---- | :---- |
| <ins>00.03</ins> |  |  |  |
| 00.02 | <ins>#2026m09d28</ins> |  | <ins>Draft — Design Review and approval pending. Minor revision (design change during development, component not released: no DCR required). REQ-0004 and REQ-0010 extended to the consecutive-positive cluster behaviour (anchor cluster length, number of clustered positives per series, median per point; NaN breaks adjacency). New SPEC-0004.1; SPEC-0010, 0011 and 0010.1 (TC-12 renumbering) updated. New RISK-0004.1 (residual Medium, open verification actions); RISK-0010 updated. Verification Summary 223/223 (2026-09-28). Adjacency rule added to Parameters. Applied procedures: P26.0039, P26.0018, P26.0027 Rev 00.01 (confirmed 2026-09-28).</ins> |
| 00.01 | #2026m09d24 |  | Draft — Design Review and approval pending. Minor revision (design change during development, component not released: no DCR required). SR 0001–0010 aligned to the Rev 00.01 implementation: all positives &gt;= threshold, per-anchor descent windows with next_positive closure, per-(visit, point, anchor) output granularity, csv/excel ingestion with data-quality rules, per-visit batch orchestration. REQ-0011 and SPEC-0012 declared Obsolete (M11 removed on 2026-09-24). New TS 0001.1, 0002.1, 0002.2, 0010.1; all TS and Verification Methods updated from code. Risk Analysis updated, new RISK 0002.1 and 0010.1. Verification Summary added. Parameters updated (epsilon 1.0, n_max 1000). Document information and references corrected. Applied procedures: P26.0039, P26.0018, P26.0027 Rev 00.01 (confirmed). |
| 00.00 | \#2026m08d26 | \[IR\] | First edition. Technical Specifications (SPEC-CPM-IA-P26.0001–0012), ISO 14971 Risk Analysis and fixed Parameters reverse-engineered from the implemented source code. |

    2. **Authors, Contributors & Reviewers** 

| Name & Surname  \[Name Acronymus\] | Role:  \[Authors, Contributors, Reviewers, Approver\] |
| :---- | :---- |
| Ilaria Rocco \[IR\] |  Author |
|  |  |
|  |  |

    3. **Signatures & Approvals**

for Math Biology,

City

| Date | Name & Surname   | Role | Signature |
| :---- | :---- | :---- | :---- |
| \#yyyymMMdDD  |  | s |  |
|   |  |  |  |
|   |  |  |  |

for \<XXX OTHER PARTIES\>

City

| Date | Name & Surname   | Role | Signature |
| :---- | :---- | :---- | :---- |
|   |  |  |  |
|   |  |  |  |
|   |  |  |  |

