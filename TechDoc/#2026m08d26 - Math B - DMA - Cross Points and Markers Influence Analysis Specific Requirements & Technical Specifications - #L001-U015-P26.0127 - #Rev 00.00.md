 

# 

# **Math B \- DMA \- Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications**

## 

## Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications

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

[**9\. Parameters	6**](#parameters)

[**10\. Document Governance	8**](#document-governance)

[10.1. Revision List & Notes	8](#revision-list-&-notes)

# 

1. # **Document Information**

| Doc. Title. | DMA \- Cross Points and Markers Influence Analysis Specific Requirements & Technical Specifications |
| :---- | :---- |
| Doc ID | \#PT-L01-U000-P26.xxxx |
| Doc Type | requirements & technical specification |
| Department  &/or Processes Area | R\&D |
| Effective Date | 26 August 2026 |
| Current Revision | 00.00 |
| Short Doc Code | \[CPM-IA\] |

# 

2. # **Definitions & Acronyms** 

| Def. / Acron. | Description |
| :---- | :---- |
|  Math B | Math Biology |
| DMA  | Deep Metabolic-process Assessment |
|  |  |
|  |  |
|  |  |

3. # **Referencies**

Unless otherwise specified, definitions and acronyms are defined in DOC-QMS-001 – Definitions, Acronyms & Ontology.

| Ref. | Doc ID | Description or Link |
| :---- | :---- | :---- |
| ref.1 | \#L001-U001-P26.0007 | Math B \- Definitions, Acronyms & Ontology |
| ref.2 | \#L001-U015-P26.0020 | Math B \- DMA \- Hardware & Software Components Tree & Accessory \- Registry |
| ref.3 | \#L001-U015-P26.0018 | Math B \- Procedure \- Protocols & IDs \- Revisions and Versioning and Status |
| ref.4 | \#L001-U015-P26.0039 | Math B \- Procedure Requirements, Technical Specification & Design Traceability Matrix \- Principles |
| ref.5 | \#L001-U015-P26.0035 | Math B \- DMA Screening \- General Hardware & Software Requirements |
| ref.6 | \#L001-U015-P26.0033 | Math B \- DMA Screening \- Design Traceability Matrix (DTM) \- MDR Class I |

4. # **Introduction (Purpose & Scope)**

This document defines the Cross Points and Markers Influence Analysis Specific Requirements (SR) and Technical Specifications (TS) for the DMA Screening system, a Class I medical device developed by Math Biology S.r.l. for the non-invasive acquisition of quasi-static bioelectrical surface currents. 

The document is produced in accordance with the Quality Management System requirements of ISO 13485:2016 and the applicable provisions of EU Regulation 2017/745 (MDR). It constitutes a formal design output record within the DMA Screening History File and provides the foundational input for the Design Traceability Matrix (DTM, ref.6). Requirements derivation, identifier coding, and traceability rules applied throughout this document follow the procedures defined in ref. 3 and ref. 4\.

Each specific requirement (SR) in this document is formally linked to a higher-level General Requirement (GR), establishing a clear vertical chain of compliance as required by ISO 13485:2016 Clause 7.3. Moreover, in this documentation structure, each SR is defined with enough granularity to concurrently serve as the detailed Technical Specification (TS) for the implementation of the Cross Points and Markers Influence Analysis ensuring direct traceability for subsequent verification and validation activities (MDR Annex II, Section 3).

## 

5. # **Involved Components**

This document relates to the software components listed in the following table. For additional details about Components see **ref. 2\.**

**\[Select only the correct associated component, delete the others\]**

| Component\_ID | Versioning | Name |
| :---- | :---- | :---- |
|  |  |  |
|  |  |  |
|  |  |  |

6. # **Specific Requirements**

This section lists all Specific Requirements for the Cross Points and Markers Influence Analysis. Each SR is derived from one or more General Requirements (GR) defined in **ref.5**. 

**\[REQ-CPM-IA-P26.0001\]**

Linked to: **\[REQ-G-P26.0072\]**

**External Configuration Loading**

Requirement: The component loads all execution parameters at runtime from an external XML configuration file, with no processing parameter hardcoded in the source. The configuration provides, as a minimum: the input and output paths and the output-label suffixes; the positive-detection threshold (default 300 %); the rise tolerance ε used to close a descent window; and the maximum number of descent points N\_max. A missing or malformed configuration file results in a controlled failure of the run.

**\[REQ-CPM-IA-P26.0002\]**

Linked to: **\[REQ-G-P26.0084\]**

**Autonomous Raw-Variation Ingestion**

Requirement: The component operate autonomously on the consolidated raw percentage-variation dataset produced by the Raw Variation Computation component, ingesting it as a long-format table in which every record identifies a visit, a marker and an anatomical point, together with its raw percentage variation and the associated visit metadata. The component validates the presence of the required fields and doesn’t require input from any other component to complete its computation.

**\[REQ-CPM-IA-P26.0003\]**

Linked to: **\[REQ-G-P26.0018\]**

**Marker Sequence Reconstruction**

Requirement: For each (visit, anatomical point) pair, the component reconstructs the ordered sequence of marker measurements that defines the analysis axis along which cross-marker influence is evaluated. The marker acquisition order must be derived deterministically from the order of first appearance of each marker in the input dataset and applied consistently to every (visit, point) series, so that the notions of measurement “preceding” and “subsequent” to a given marker are unambiguously defined.

**\[REQ-CPM-IA-P26.0004\]**

Linked to: **\[REQ-G-P26.0018\]**

**First-Positive Trigger Detection**

Requirement: Within each (visit, point) marker sequence, the component detects the first marker whose raw percentage variation exceeds the configured positive-detection threshold (default 300 %) and shall designate it as the first positive, i.e. the excitation onset, for that series. Only the first threshold-exceeding marker serves as the anchor for the subsequent influence analysis; later threshold-exceeding markers must not define new anchors. A series containing no threshold-exceeding marker must be reported as having no cross-marker effect.

**\[REQ-CPM-IA-P26.0005\]**

Linked to: **\[REQ-G-P26.0018\]**

**Positive Census Across Points**

Requirement: The component determines, across the whole dataset, how many and which anatomical points present at least one first positive, providing both the count and the identity of the positive points as an explicit output. This census must enable quantification of the prevalence of the cross-marker excitation phenomenon at anatomical-point level.

**\[REQ-CPM-IA-P26.0006\]**

Linked to: **\[REQ-G-P26.0018\]**

**Adaptive Descent-Window Determination**

Requirement: Starting from the first positive of each (visit, point) series, the component determines the influence (descent) window as the anchor followed by the maximal initial run of non-increasing consecutive marker measurements. The window must be closed at the first significant rise — defined as the first consecutive increase exceeding the configured rise tolerance ε — which marks the end of the positive’s influence, and shall in any case be truncated to at most N\_max points to prevent an excessively long descent. The number of points retained must therefore be adaptive to the actual length of the descent preceding the rise.

**\[REQ-CPM-IA-P26.0007\]**

Linked to: **\[REQ-G-P26.0018\]**

**Descent Slope Computation**

Requirement: For each (visit, point) series with an identified descent window, the component computes the slope (rate of decrease) of the descending curve over that window, treating the marker positions as equally spaced abscissae. The slope must be obtained by the standard least-squares linear-regression estimate over the window’s points, so that the resulting value expresses the average percentage-point change per marker step; for a minimal window of two points this estimate coincides with the elementary secant slope.

**\[REQ-CPM-IA-P26.0008\]**

Linked to: **\[REQ-G-P26.0018\]**

**Descent Shape Descriptors**

Requirement: In addition to the slope, the component compute descriptors characterising the descending curve after the first positive, comprising, as a minimum: the descent depth (difference between the anchor value and the minimum value within the window), the descent length (number of points in the window), and the mean per-step decrease. These descriptors must quantify the magnitude and the extent of the excitation decay.

**\[REQ-CPM-IA-P26.0009\]**

Linked to: **\[REQ-G-P26.0018\]**

**Pre/Post Positive Variance Indicator**

Requirement: For each (visit, point) series with a first positive, the component compute a dispersion indicator of the marker measurements before and after the anchor, where the “before” segment comprises the markers preceding the first positive in the sequence and the “after” segment comprises the markers within the descent window. The indicator must be expressed as the statistical variance of each segment, enabling comparison of measurement dispersion prior to and following the excitation. The component additionally reports the normalised variance\_ratio \= variance\_after / variance\_before as a comparative dispersion indicator, which is undefined (None) when either variance cannot be computed or the pre-anchor variance is zero.

**\[REQ-CPM-IA-P26.0010\]**

Linked to: **\[REQ-G-P26.0031\]**

**Consolidated Tidy Output and Per-Point Aggregation**

Requirement: The component consolidate its results into tidy (long-format) outputs at two levels: a per-(visit, point) record carrying the first-positive anchor, the descent-window characteristics (slope, depth, length, mean per-step decrease) and the pre/post variance indicators; and a per-point aggregation across all visits summarising the prevalence of positives and the central tendency (e.g. median) of the descent metrics. Each output record must be uniquely identified by its grouping keys together with the relevant visit metadata.

**\[REQ-CPM-IA-P26.0011\]**

Linked to: **\[REQ-G-P26.0022\], \[REQ-G-P26.0028\], \[REQ-G-P26.0029\]**

**Automated Run Report Generation**

Requirement: The component shall generate a formatted PDF run report summarising the analysis results — run parameters, series- and point-level positivity statistics, per-point prevalence and descent medians, and an anchor-marker summary — assembled through a programmatic templating engine (LaTeX / pdflatex) that enforces a fixed, auditable layout. Report generation shall fail in a controlled manner and shall not overwrite an existing report. All report text shall use non-diagnostic language. 

7. # **Technical Specification**

This section provides the Technical Specification for each Specific Requirement defined in Section 6\. 

**\[SPEC-CPM-IA-P26.0001\]**

Linked to: **\[REQ-CPM-IA-P26.0001\]**

**External Configuration Loading**

Specification: config\_loader.load\_config() parses the XML configuration via xml.etree.ElementTree into an immutable CpmIaConfig dataclass. Required elements: input\_path, output\_path, output\_label\_detail, output\_label\_aggregated, rise\_tolerance\_epsilon (float) and n\_max (int); threshold\_pct is optional with default 300.0. A missing file, malformed XML, or a blank/uncastable value raises ConfigurationError, aborting the run with no partial processing. No processing parameter is hardcoded in the source.

Verification Method: Automated unit test tests/test\_config\_loader.py (valid load, missing element, malformed XML, invalid cast, default injection).

**\[SPEC-CPM-IA-P26.0002\]**

Linked to: **\[REQ-CPM-IA-P26.0002\]**

**Autonomous Raw-Variation Ingestion**

Specification: data\_ingestion.load\_data() reads the UTF-8 CSV at config.input\_path, requiring the columns visit\_id, marker, point, percentage\_variation and visit\_date. percentage\_variation is coerced to float64 (genuine NaN is preserved as a missing measurement while non-numeric text is rejected); a NaN in any key column (visit\_id, marker, point) raises IngestionError, as do a non-.csv suffix or a missing file. The module completes without input from any other running component.

Verification Method: Automated unit test tests/test\_data\_ingestion.py (schema pass, missing column, non-numeric value, NaN key, wrong suffix).

**\[SPEC-CPM-IA-P26.0003\]**

Linked to: **\[REQ-CPM-IA-P26.0003\]**

**Marker Sequence Reconstruction**

Specification: marker\_sequence.build\_sequences() derives, per visit, the marker order as the order of first appearance within that visit's rows (dict.fromkeys over a groupby with sort=False — never sorted(), set() or unique()), and builds per-(visit, point) value sequences aligned to that order, filling absent markers with float('nan'). Exact duplicate rows are dropped; a repeated (visit, point, marker) triplet carrying different values raises SequenceError.

Verification Method: Automated unit test tests/test\_marker\_sequence.py (per-visit order immutability, NaN fill, duplicate collapse, value-conflict error).

**\[SPEC-CPM-IA-P26.0004\]**

Linked to: **\[REQ-CPM-IA-P26.0004\]**

**First-Positive Trigger Detection**

Specification: trigger\_detection.detect\_triggers() scans each sequence in per-visit order and designates the first marker whose value strictly exceeds threshold\_pct as the anchor (first positive), recording its marker, index and value and stopping at the first hit; NaN positions are skipped and later threshold-crossing markers never create a new anchor. Series with no exceeding marker are flagged no\_cross\_marker\_effect \= True. threshold\_pct \<= 0 raises TriggerError.

Verification Method: Automated unit test tests/test\_trigger\_detection.py (first-hit anchoring, later-crossing ignored, NaN skip, no-effect flag, invalid threshold).

**\[SPEC-CPM-IA-P26.0005\]**

Linked to: **\[REQ-CPM-IA-P26.0005\]**

**Positive Census Across Points**

Specification: positive\_census.compute\_census() aggregates the trigger results to anatomical-point level, returning an immutable PointCensus with positive\_point\_count, a sorted positive\_points list, and total\_point\_count. A point is positive when at least one (visit, point) series has no\_cross\_marker\_effect \= False. Empty input returns a zero census.

Verification Method: Automated unit test tests/test\_positive\_census.py (count and identity, deterministic sorting, empty input).

**\[SPEC-CPM-IA-P26.0006\]**

Linked to: **\[REQ-CPM-IA-P26.0006\]**

**Adaptive Descent-Window Determination**

Specification: descent\_window.determine\_descent\_windows() builds, from each anchor, the maximal run of consecutive non-increasing values, closing the window at the first rise where (val \- prev) \> rise\_tolerance\_epsilon and capping the length at n\_max (truncated\_by\_n\_max \= True when the cap fires before a natural close). NaN values are bridged (skipped, prev retained). Series with no anchor return None. n\_max \< 1 or rise\_tolerance\_epsilon \< 0 raises DescentError.

Verification Method: Automated unit test tests/test\_descent\_window.py (natural close on rise, epsilon tolerance, n\_max truncation, NaN bridging, boundary errors).

**\[SPEC-CPM-IA-P26.0007\]**

Linked to: **\[REQ-CPM-IA-P26.0007\]**

**Descent Slope Computation**

Specification: descent\_slope.compute\_slopes() computes the ordinary-least-squares slope over each descent window using equally spaced abscissae x \= 0..L-1 and the closed form slope \= (n\*Sum(i\*yi) \- Sum(i)\*Sum(yi)) / (n\*Sum(i^2) \- (Sum(i))^2). Single-point windows return None; a NaN inside a window raises SlopeError. For a two-point window the estimate coincides with the elementary secant slope.

Verification Method: Automated unit test tests/test\_descent\_slope.py, including numerical cross-validation of the closed form against numpy.polyfit.

**\[SPEC-CPM-IA-P26.0008\]**

Linked to: **\[REQ-CPM-IA-P26.0008\]**

**Descent Shape Descriptors**

Specification: descent\_descriptors.compute\_descriptors() returns, per window, descent\_depth \= anchor\_value \- min(window\_values), descent\_length \= number of points in the window, and mean\_per\_step\_decrease \= depth / (length \- 1\) (0.0 when length \== 1). None is returned for series without a window; a missing anchor value or a NaN in the window raises DescriptorError.

Verification Method: Automated unit test tests/test\_descent\_descriptors.py (depth, length, mean-per-step, single-point case, error paths).

**\[SPEC-CPM-IA-P26.0009\]**

Linked to: **\[REQ-CPM-IA-P26.0009\]**

**Pre/Post Positive Variance Indicator**

Specification: variance\_indicator.compute\_variance\_indicators() computes the sample variance (statistics.variance, ddof \= 1\) of the pre-anchor segment (sequence values preceding the anchor, NaN removed) and of the post-anchor segment (the descent-window values). It additionally reports variance\_ratio \= variance\_after / variance\_before. Each variance is None when its cleaned segment holds fewer than two points; variance\_ratio is None when either variance is None or variance\_before \== 0; the whole entry is None when no\_cross\_marker\_effect \= True.

Verification Method: Automated unit test tests/test\_variance\_indicator.py, including case TC-09-010 covering variance\_ratio.

**\[SPEC-CPM-IA-P26.0010\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Consolidated Tidy Detail Output**

Specification: output\_consolidation.\_build\_detail() emits a per-(visit, point) tidy (long-format) table joining the visit metadata with ten analytical columns (first\_positive\_marker, first\_positive\_value, no\_cross\_marker\_effect, descent\_slope, descent\_depth, descent\_length, mean\_per\_step\_decrease, variance\_before, variance\_after, variance\_ratio). Unique (visit, point) identification is enforced after the metadata join; a join failure or a duplicate key raises OutputError. The file is written to {output\_path}/{output\_label\_detail}.csv.

Verification Method: Automated unit test tests/test\_output\_consolidation.py (detail schema and column order, key uniqueness, join-failure error).

**\[SPEC-CPM-IA-P26.0011\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Per-Point Aggregation Output**

Specification: output\_consolidation.\_build\_aggregation() emits a per-point aggregation table with total\_visit\_count, positive\_visit\_count, the medians over positive visits of descent\_slope, descent\_depth, descent\_length and mean\_per\_step\_decrease, and positive\_prevalence. Pre-existing output files are never overwritten (OutputError, G-10) and an internal census cross-check logs a warning on divergence. The file is written to {output\_path}/{output\_label\_aggregated}.csv.

Verification Method: Automated unit test tests/test\_output\_consolidation.py (aggregation medians, prevalence, no-overwrite guard).

**\[SPEC-CPM-IA-P26.0012\]**

Linked to: **\[REQ-CPM-IA-P26.0011\]**

**Automated PDF Run Report**

Specification: report\_generator.generate\_report() fills the LaTeX template data/templates/cpm\_ia\_report.tex.template with run statistics and per-point tables, escaping LaTeX special characters and stripping C1 control characters, then compiles the source to PDF with two pdflatex passes (correct table-of-contents page numbers). The .tex source is always written and preserved on failure; a missing template, an absent pdflatex, a compilation failure, or a pre-existing PDF raises ReportError. The anchor-summary table applies a fixed presentation threshold of 3.5 % (rows with anchor\_pct \>= 3.5). NOTE: this 3.5 % constant is currently hardcoded in report\_generator.py and is recorded in the Parameters chapter as a fixed presentation constant.

Verification Method: Automated unit test tests/test\_report\_generator.py (cases TC-11-001 to TC-11-018: template fill, LaTeX escaping, pdflatex invocation, error paths).

8. # **Risk Analysis**

This section provides the Risk Analysis entries for each Specific Requirement, in compliance with ISO 14971 and ref.4. For each risk, severity × probability establishes the initial risk level; the mitigation link identifies the SR/TS providing the control; residual risk is stated after mitigation.

**\[RISK-CPM-IA-P26.0001\]**

Linked to: **\[REQ-CPM-IA-P26.0001\]**

**Execution with unintended parameters**

Risk: Hazard: the analysis runs on wrong thresholds because a malformed or partial configuration is accepted, producing a misleading non-clinical indication. Cause: silent acceptance of an invalid config. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: fail-closed validation of every required field with a controlled ConfigurationError abort (SPEC-CPM-IA-P26.0001). Residual risk: Low.

**\[RISK-CPM-IA-P26.0002\]**

Linked to: **\[REQ-CPM-IA-P26.0002\]**

**Corrupted or mistyped input data admitted**

Risk: Hazard: non-numeric or key-missing records enter the computation, corrupting downstream metrics. Cause: absent schema validation. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: mandatory schema and type validation at ingestion with IngestionError on any violation (SPEC-CPM-IA-P26.0002). Residual risk: Low.

**\[RISK-CPM-IA-P26.0003\]**

Linked to: **\[REQ-CPM-IA-P26.0003\]**

**Marker order corrupted**

Risk: Hazard: the notions of preceding and subsequent marker are inverted, so cross-marker influence is attributed to the wrong marker. Cause: reordering the sequence by sorting instead of first-appearance order. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: deterministic first-appearance ordering per visit, explicitly forbidding sort/set/unique, unit-tested for immutability (SPEC-CPM-IA-P26.0003). Residual risk: Low.

**\[RISK-CPM-IA-P26.0004\]**

Linked to: **\[REQ-CPM-IA-P26.0004\]**

**Incorrect excitation-onset anchoring**

Risk: Hazard: a later threshold-crossing marker is chosen as the anchor, shifting the entire influence analysis and producing a misleading indication. Cause: failure to stop at the first positive. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: strict first-hit break with explicit no-effect flagging, unit-tested (SPEC-CPM-IA-P26.0004). Residual risk: Low.

**\[RISK-CPM-IA-P26.0005\]**

Linked to: **\[REQ-CPM-IA-P26.0005\]**

**Misstated prevalence of the phenomenon**

Risk: Hazard: the count or identity of positive anatomical points is wrong, misrepresenting how widespread the cross-marker effect is. Cause: duplicate or missed points in aggregation. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: set-based unique counting with deterministic sorted output, cross-checked against the aggregation table (SPEC-CPM-IA-P26.0005). Residual risk: Low.

**\[RISK-CPM-IA-P26.0006\]**

Linked to: **\[REQ-CPM-IA-P26.0006\]**

**Descent window mis-delimited**

Risk: Hazard: the influence window is too long or too short, distorting every descent metric derived from it. Cause: wrong rise-tolerance handling or missing length cap. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: epsilon-based closure at the first significant rise and a hard n\_max cap with truncation flagging, unit-tested (SPEC-CPM-IA-P26.0006). Residual risk: Low.

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

Risk: Hazard: the pre/post variance comparison is undefined or misleading when a segment is too short or invariant. Cause: variance computed on fewer than two points or division by a zero baseline. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: sample variance guarded to require at least two points and variance\_ratio suppressed (None) when the pre-anchor variance is zero (SPEC-CPM-IA-P26.0009). Residual risk: Low.

**\[RISK-CPM-IA-P26.0010\]**

Linked to: **\[REQ-CPM-IA-P26.0010\]**

**Output ambiguity or silent overwrite**

Risk: Hazard: results are not uniquely identifiable or a prior run's output is silently destroyed, breaking traceability. Cause: duplicate keys after join or overwriting existing files. Initial risk: Severity 3 x Probability 2 \= Medium. Mitigation: enforced (visit, point) uniqueness and a no-overwrite guard, both raising OutputError (SPEC-CPM-IA-P26.0010/ .0011). Residual risk: Low.

**\[RISK-CPM-IA-P26.0011\]**

Linked to: **\[REQ-CPM-IA-P26.0011\]**

**Non-compliant or corrupted report output**

Risk: Hazard: the run report is malformed, silently overwrites a prior report, or renders unescaped content, undermining the auditability of the output. Cause: template/compilation failure or missing collision guard. Initial risk: Severity 2 x Probability 2 \= Low. Mitigation: LaTeX escaping, controlled ReportError on template/pdflatex failure, and a no-overwrite guard; non-diagnostic language per REQ-G-P26.0022/0028 applies to all report text (SPEC-CPM-IA-P26.0012). Residual risk: Low.

9. # **Parameters**

This section contains all the fixed default parameters for the Cross Point and Markers Influence Analysis.

| Parameter | Value | Description |
| :---- | :---- | :---- |
| threshold\_pct | 300.0 | Positive-detection threshold (%). Fixed by SPEC-CPM-IA-P26.0001; applied in SPEC-CPM-IA-P26.0004. |
| rice\_tolerance\_epsilon | 5.0 | Maximum consecutive increase (percentage points) tolerated before a descent window closes. SPEC-CPM-IA-P26.0001 / 0006\. |
| n\_max | 10 | Maximum descent-window length (points). SPEC-CPM-IA-P26.0001 / 0006\. |
| anchor-summary threshold | 3.5 | Fixed report presentation constant (%): anchor rows with anchor\_pct \>= 3.5 are listed. Owned by SPEC-CPM-IA-P26.0011. Currently hardcoded in report\_generator.py rather than sourced from the XML config. |
|  |  |  |
|  |  |  |
|  |  |  |

# 

# 

10. # **Document Governance**

    1. ## **Revision List & Notes** 

| Revisision  | Date | Approved By \-  Name Acronymus | Notes |
| :---- | :---- | :---- | :---- |
| 00.02 |  |  |  |
| 00.01 |  |  |  |
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

