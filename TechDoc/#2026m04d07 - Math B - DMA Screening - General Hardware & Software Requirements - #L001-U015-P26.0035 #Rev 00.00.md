 

# 

# **Math B \- DMA Screening \- General Hardware & Software Requirements**

## 

## General Hardware, Firmware & Software Requirements

# 

# **TABLE OF CONTENTS**

[**1\. Document Information	3**](#document-information)

[2\. Definitions & Acronyms	3](#definitions-&-acronyms)

[3\. Referencies	3](#referencies)

[**4\. Introduction	5**](#introduction)

[**5\. Hardware General Requirements List	5**](#hardware-general-requirements-list)

[5.1. Physical Characteristics	5](#5.1.-physical-characteristics)

[5.2. Electrical & Power	6](#5.2.-electrical-&-power)

[5.3. Sensors & Measurement	7](#5.3.-sensors-&-measurement)

[5.4. Device & Physical Component Traceability	7](#5.4.-device-&-physical-component-traceability)

[**6\. Firmware General Requirements List	7**](#firmware-general-requirements-list)

[6.1. Software Version Control	7](#6.1.-software-version-control)

[6.2. Functional Requirements	7](#6.2.-functional-requirements)

[**7\. Software General Requirements List	8**](#software-general-requirements-list)

[7.1. DMA Visit APP	8](#7.1.-dma-visit-app)

[7.1.1. High-Level System Requirements	8](#7.1.1.-high-level-system-requirements)

[7.1.2. User Interface (UI) & Usability Requirements	9](#7.1.2.-user-interface-\(ui\)-&-usability-requirements)

[7.1.3. Visit Control and Data Acquisition	10](#7.1.3.-visit-control-and-data-acquisition)

[7.1.4. Reporting and Data Visualization	11](#7.1.4.-reporting-and-data-visualization)

[7.1.5. Data Management and Security	12](#7.1.5.-data-management-and-security)

[7.2. DMA Device Data Stream Acquisition	13](#7.2.-dma-device-data-stream-acquisition)

[7.2.1 System Orchestration and Core Control	15](#7.2.1-system-orchestration-and-core-control)

[7.2.2. Network Communication and Client Management	17](#7.2.2.-network-communication-and-client-management)

[7.2.3 Utility & Configuration Functions	18](#7.2.3-utility-&-configuration-functions)

[7.3. DMA Sync Services Device (Edge) \- Cloud	18](#7.3.-dma-sync-services-device-\(edge\)---cloud)

[7.4. DMA Data Model Design &  Sync Services	20](#7.4.-dma-data-model-design-&-sync-services)

[7.5. DMA Algorithms	22](#7.5.-dma-algorithms)

[7.6. Report Generation & Signature Requirements	22](#7.6.-report-generation-&-signature-requirements)

[**8\. Cybersecurity General Requirements	23**](#cybersecurity-general-requirements)

[**9\. Document Governance	26**](#document-governance)

[9.1. Revision List & Notes	26](#revision-list-&-notes)

# 

1. # **Document Information** {#document-information}

| Doc. Title. | DMA Screening \- Hardware & Software Requirements |
| :---- | :---- |
| Doc ID | \#L001-U015-P26.0035 |
| Doc Type | Technical Documentation |
| Processes Area | Quality Management System |
| Effective Date | 07 April 2026 |
| Current Revision | 00.00 |

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
| ref.2 | \#L001-U015-P26.0033  | Math B \- DMA Screening \- Design Traceability Matrix (DTM) \- MDR Class I  |
| ref.3 | \#L001-U015-P26.0039 | Math B \- SOP \- Requirements, Technical Specification & Design Traceability Matrix \- Principles   |
| ref.4 | \#L001-U015-P26.0018 | Math B \- Procedure \- Protocols & IDs \- Revisions and Versioning  and Status |
|  |  |  |

4. # **Introduction**  {#introduction}

The DMA® Screening device's Hardware, Firmware, and Software General Requirements are detailed in this document, all of which are derived from its Intended Use and User Needs. This document covers all DMA® Screening components General Requirements (see **ref.1, 3** for definition and instructions). General Requirements (GR) are defined as the high-level parent requirements, applicable to the entire device or a main component group. Specific Requirements (SRs), in contrast, are the detailed, mandatory requirements unique to a single submodule or software application and are derived from the GRs. General Requirements may sometimes coincide with Specific Requirements. To ensure traceability, where possible, this document links the single component Requirements & Specification documents that contain the detailed list of associated Specific Requirements and Technical Specifications. The complete list of all these traceability links is stored in the Design Traceability Matrix (**DTM**) (see **ref.2**). *This structure guarantees that every General Requirement is paired with a corresponding Specific Requirement and consequently with a Technical Specification.*

To ensure traceability to design outputs, each general requirement is assigned a unique ID (see **ref.4**). The established format for General Requirement is: **\[REQ-G-Pyy.XXXX\]**. 

5. # **Hardware General Requirements List** {#hardware-general-requirements-list}

   ## **5.1. Physical Characteristics** {#5.1.-physical-characteristics}

**\[REQ-G-P26.0001\]: DMA Device Dimensions, Weight, Materials, Finish**

Requirement: The DMA Device shall have dimensions of 17.5 cm x 17.5 cm x 5 cm and weigh no more than 500 grams. It shall be constructed from a combination of ABS plastic for the housing and stainless steel for internal components to ensure durability, with a IP23 protection grade.  
Rationale: Ensures the device is portable, durable, and meets user handling requirements.

**\[REQ-G-P26.0002\]: General DMA Probe Design and Functional Requirements**

Requirement: The DMA probe shall be a handheld, high-sensitivity sensor designed to acquire quasi-static bioelectrical surface currents (nA range). It shall feature a 3D-printed Nylon PA12 housing with a Soft Touch Black finish. The probe must exert a constant, adjustable pressure on the skin between 100g and 200g. The measurement tip shall use AgCl/Ag or validated metallic equivalents and must be compatible with conductive gel or physiological saline solutions. For industrialization (V3.1), the tip shall be conical to facilitate precise point localization, and the assembly shall utilize a bayonet locking system and clip-based internal connections for tool-less maintenance.

Rationale: Nylon PA12 provides the necessary mechanical durability and biocompatibility for medical-grade certification. Constant pressure is critical to ensure measurement repeatability, as current readings are pressure-dependent. The conical tip and simplified assembly (bayonet/clips) address previous usability issues where flat tips made it difficult to find measurement points on small anatomical areas (e.g., children's fingers) and soldered wires were prone to mechanical failure.

**\[REQ-G-P26.0003\]: Environmental conditions**

Requirement: The device shall operate within an ambient temperature range of 10°C to 40°C and humidity levels up to 85%. It shall have an IP rating of at least IP23 for protection against dust and water ingress.  
Rationale: Ensures the device can function reliably in various environmental conditions.

**\[REQ-G-P26.0004\]: RoHS Directive Compliance**

Requirement: The DMA device and all its constituent components (including PCB, connectors, cables, and electronic parts) shall comply with the EU Directives. The device shall not contain restricted substances (such as Lead, Mercury, Cadmium, or specific Phthalates) in concentrations above the permitted thresholds.

Rationale: Ensures environmental safety and regulatory compliance for commercialization in the European market. 

## **5.2. Electrical & Power** {#5.2.-electrical-&-power}

**\[REQ-G-P26.0005\]: Voltage, Current, Battery Specs, Power Consumption, LED**

Requirement: The DMA electronic device shall operate on a 5V DC power supply with a maximum current draw of 1 A, powered by an usb cable connected to a PC. A power led is required in order to indicate when the device is when the device is turned on.  
Rationale: Ensures the device can operate reliably under various conditions and provides sufficient runtime for testing sessions. The LED helps the operator to know when the device is turned on.

**\[REQ-G-P26.0006\]: Electrical Isolation**

Requirement: The device shall include a galvanic isolator for the USB connection with a minimum insulation rating of 3000V.

Rationale: Protects the patient from potential electrical faults in the host PC, ensuring the device remains a "passive" instrument with a maximum voltage of 5V.

**\[REQ-G-P26.0007\]: Electromagnetic Compatibility (EMC) Compliance**

Requirement: The DMA device shall comply with the EN 61326-1:2013 standard for electrical equipment for measurement, control, and laboratory use. 

Rationale: Ensures the device operates correctly in clinical or laboratory environments without being affected by other electronic equipment (e.g., PCs, medical monitors) and without emitting interference that could disturb nearby sensitive instruments.

## **5.3. Sensors & Measurement** {#5.3.-sensors-&-measurement}

**\[REQ-G-P26.0008\]: Sensor Type, Accuracy, Range, Sampling Rate**

Requirement: The DMA probe shall detect bioelectrical signals with an accuracy of ±0.1% (comparable to a laboratory multimeter) and a measurement range up to 16000 nA. It shall sample at a rate of 10 Hz.  
Rationale: Ensures precise current measurement for accurate screening results.

## **5.4. Device & Physical Component Traceability** {#5.4.-device-&-physical-component-traceability}

**\[REQ-G-P26.0009\]: Device & Component Traceability**

Requirement: Each device shall be identified by its Microcontroller MAC Address and each probe by an internal passive RFID/NFC tag.

Rationale: Ensures unique identification for quality control and tracking of measurement sessions within the clinical database.

6. # **Firmware General Requirements List** {#firmware-general-requirements-list}

   ## **6.1. Software Version Control** {#6.1.-software-version-control}

**\[REQ-G-P26.0010\]: Firmware Versioning and Update Protocol**

Requirement: The firmware version shall be formatted as "vX.Y.Z" (where X \= major release, Y \= minor release, and Z \= patch level). Updates shall be installed via a secure wired connection (USB) through the host PC to the Teensy 4.0 microcontroller.

Rationale: Standardized Semantic Versioning ensures consistent software management and compatibility tracking between the probe hardware and the analysis app. Since the DMA is a passive device powered and managed via USB, a wired update protocol ensures a stable and secure data transfer environment for critical firmware flashes without requiring additional wireless hardware.

## **6.2. Functional Requirements** {#6.2.-functional-requirements}

**\[REQ-G-P26.0011\]: Data Acquisition & Processing**

Requirement: The firmware shall include algorithms for real-time bioelectrical signal acquisition and processing. It must support data structures compatible with data export in ‘.xlsx’ format.  
Rationale: Ensures accurate data collection and ease of use.

**\[REQ-G-P26.0012\]: Serial Communication Protocol**

Requirement: The device shall establish bidirectional communication with the host PC via a Virtual COM Port (VCP) over USB. The communication shall be configured with a baud rate of 38,400 bps. The data stream shall include real-time acquisition values, probe button status, and range/scale selector position.

Rationale: A standardized serial protocol over USB ensures compatibility across different operating systems without the need for custom hardware drivers. The 38,400 baud rate provides sufficient bandwidth for the high-frequency sampling (10 samples per point) required to ensure measurement stability and noise filtering.

**\[REQ-G-P26.0013\]: Hardware-in-the-loop Self-Test**

Requirement: The firmware shall support a pre-check routine using an onboard Test Point (constant current generator in the 100–400 nA range) to verify probe and box functionality before use.

Rationale: Allows the operator to confirm the system is calibrated and the probe tip/wire are intact before clinical trials.

**\[REQ-G-P26.0014\]: Automatic Scale Switching**

Requirement: The system shall implement an automatic switch between measurement scales when signal levels approach the limits of the current range.

Rationale: Prevents data loss due to saturation, especially when using high-conductivity electrodes.

7. # **Software General Requirements List** {#software-general-requirements-list}

   ## **7.1. DMA Visit APP** {#7.1.-dma-visit-app}

The requirements for the DMA Visit APP, are divided into its single subcomponent in order to keep trace of every stage of the data acquisition protocol & user interface.

### **7.1.1. High-Level System Requirements** {#7.1.1.-high-level-system-requirements}

**\[REQ-G-P26.0015\]: Data Synchronization and Offline Capability**

Requirement:The DMA Local App shall implement a secure, bi-directional data synchronization module with the Cloud Server, and must be designed to allow for independent data acquisition and local storage even when connectivity to the server is unavailable.

Rationale:Ensures operational continuity in any environment (MDR GSPR 17.1) and prevents the loss of critical patient data (ISO 13485:2016, 4.2.4).

**\[REQ-G-P26.0016\]**: **GDPR Compliance and Data Security**

Requirement: The entire software system (Local App and Cloud Server) shall protect sensitive personal data (e.g., name, surname) via encryption and strict adherence to the General Data Protection Regulation (GDPR).

Rationale: Essential legal requirement for patient confidentiality and compliance with GSPRs related to protection (MDR Annex I, 17.2).

**\[REQ-G-P26.0017\]: Visit Management Functionality**

Requirement: The DMA V-App shall provide essential functions for the operator (Drs), including user authentication, association with the DMA Center, and full management of the visit workflow, from patient search to the start of the anamnesis/acquisition process.

Rationale: Guarantees controlled access and complete traceability of the operator performing the exam, which is fundamental for Quality (ISO 13485\) and clinical traceability.

### **7.1.2. User Interface (UI) & Usability Requirements** {#7.1.2.-user-interface-(ui)-&-usability-requirements}

**\[REQ-G-P26.0019\]: User Authentication and Profile Management**

Requirement: The Log-in component shall provide access via username/password and must support alternative biometric or external authentication (e.g., Apple/Google, SPID \- if implemented). Upon successful login, the system must recognize and apply the user’s profile (Doctor, Assistant, Researcher, Superuser), restricting access to functionalities based on the associated permissions.

Rationale: Guarantees controlled access, ensuring that only qualified personnel (Drs: Doctors/Biologics) can initiate and manage the visit process, satisfying the traceability and security requirements of MDR Annex I, 17.2 and ISO 13485 (6.2).

**\[REQ-G-P26.0020\]: Clear Workflow and Patient Identification**

Requirement: The UI must enforce a structured visit workflow (e.g., Log-in → Patient Identification → Anamnesis → Protocol Selection → Data Acquisition). The Patient Identification phase must support: 1\) Search via name/surname. 2\) Confirmation of patient identity by the operator, which must be logged as a "User Important Action" to ensure legal traceability. 

Rationale: A clear, sequential workflow minimizes the risk of use error and ensures critical identification steps are logged, which is a key requirement of MDR Annex I, GSPR 14 (Usability) and GSPR 23.4 (Records).

**\[REQ-G-P26.0021\]: Real-Time Data Visualization and Alerting**

Requirement: The Data-Acquisition Form must clearly display real-time measurement data using multiple visualizations simultaneously 1\) A numerical matrix (Points/Markers). 2\) A dynamic curve chart. Critical safety alerts (e.g., Saturation High/Low, Device Disconnected) must be presented with high visibility and distinct coloring. 

Rationale: High visibility and multi-modal display of data prevent operator desensitization to critical values and support informed decision-making during the procedure. This is essential for meeting MDR Annex I, GSPR 14 (Clarity and Interpretation).

**\[REQ-G-P26.0022\]: Non-Diagnostic and Controlled Language**

Requirement: All textual output in the UI and the Final Report component must adhere to the device's Intended Purpose. It must exclusively use non-diagnostic language (e.g., "Metabolic Profile," "Emission Variability," "Process Anomaly") and shall NOT use terms that imply a clinical diagnosis, specific pathology, or treatment recommendation. The system must include a clear statement or disclaimer visible to the operator regarding the non-diagnostic nature of the results. 

Rationale: This is the primary regulatory control to maintain the device's Class I classification and ensure compliance with MDR Annex I, GSPR 16 (Information Supplied by the Manufacturer), preventing clinical misuse or misinterpretation of the data.

**\[REQ-G-P26.0023\]: Hardware Status and Synchronization Indicator**

Requirement: The UI must include two distinct, continuously visible icons to report system status: 1\) Icon 1 (DMA Devices): Must indicate the status of the connection (e.g., Gray/Red for Disconnected, Green for Connected) to the DMA Electronic Device. 2\) Icon 2 (Cloud App): Must indicate the network connectivity status and synchronization activity with the Cloud Server (e.g., switching between Green and White to simulate data transfer). 

Rationale: Continuous status feedback is necessary for the operator to ensure the validity of the measurement data and the integrity of the data backup/sync process, directly supporting MDR Annex I, GSPR 14 (Usability) and GSPR 17 (Integrity).

### **7.1.3. Visit Control and Data Acquisition** {#7.1.3.-visit-control-and-data-acquisition}

**\[REQ-G-P26.0024\]: Guided Visit Workflow Enforcement**

Requirement: The DMA Visit App UI shall strictly enforce a structured, unskippable visit workflow in the sequence: Log-in \-\> Patient Identification \-\> Anamnesis/Pre-conditions \-\> Protocol Selection \-\> Data Acquisition \-\> Report.

Rationale: A clear, sequential workflow minimizes the risk of use error and ensures critical steps are performed in the correct order, which is a key requirement of MDR Annex I, GSPR 14 (Usability) and GSPR 23.4 (Records).

**\[REQ-G-P26.0025\]: Protocol Logic and Point Deletion Management**

Requirement: The system shall manage the selection of predefined protocols. If a Point is removed from the initial Screening Base Protocol, the system must ensure that this Point is also removed from any subsequent linked protocols to maintain data integrity and consistency across the entire visit.

Rationale: Ensures the rigid and traceable implementation of the device's defined Instructions for Use (MDR Annex I, GSPR 23\) and prevents measurement attempts on points already cancelled by the operator, reducing risk of use error.

**\[REQ-G-P26.0026\]: Operational Controls and Anomaly Recovery**

Requirement: During data acquisition, the system shall provide operator controls for Measure Retake (even after the first click) and Suspend Visit to manage and recover from measurement anomalies without data loss.

Rationale: Allows the operator to manage the procedure safely, ensuring data collection continues despite transient errors and supports the integrity of the measurement session (MDR Annex I, GSPR 14).

### **7.1.4. Reporting and Data Visualization** {#7.1.4.-reporting-and-data-visualization}

**\[REQ-G-P26.0028\]: Non-Diagnostic Language Control for UI and Report**

Requirement: All textual output in the UI and the Final Report component must exclusively use non-diagnostic language (e.g., "Metabolic Profile," "Emission Variability," "Process Anomaly") and shall NOT use terms that imply a clinical diagnosis, specific pathology, or treatment recommendation. A clear disclaimer regarding the non-diagnostic nature of the results must be visible.

Rationale: This is the primary regulatory control to maintain the device's Class I classification and ensure compliance with MDR Annex I, GSPR 16 (Information Supplied by the Manufacturer), preventing clinical misuse or misinterpretation of the data.

**\[REQ-G-P26.0030\]: Multi-Modal Real-Time Data Visualization**

Requirement: The Data-Acquisition Form must clearly display real-time measurement data using multiple visualizations simultaneously: a numerical matrix (Points/Markers) & a dynamic curve chart displaying measured nA currents over time.

Rationale: High visibility and multi-modal display prevent operator desensitization to critical values and support informed decision-making during the procedure, meeting MDR Annex I, GSPR 14 (Clarity and Interpretation).

**\[REQ-G-P26.0031\]: Visit and Raw Data Export**

Requirement: The system shall include functionality to export a complete visit as an Excel file, separating the data by protocol onto different sheets. The underlying firmware must support data structures compatible with this '.xlsx' export format.

Rationale: Provides verifiable raw data and results for clinical audits, Post-Market Surveillance (PMS), and internal quality checks, supporting the documentation requirements of MDR Annex II.

### **7.1.5. Data Management and Security** {#7.1.5.-data-management-and-security}

**\[REQ-G-P26.0032\]: Audit Trail for Critical Actions**

Requirement: The operator's confirmation of patient identity must be logged as a "User Important Action" to ensure legal traceability. The system shall also manage a Revision Log (Audit Trail) for changes to critical records (e.g., Anamnesis) that generates a new record while preserving the previous version, including the User ID of the operator who made the change.

Rationale: Implements an Audit Trail for critical actions and data changes, ensuring the traceability, security, and integrity of medical records as required by MDR Annex I, GSPR 17 (Protection against unauthorized access) and GSPR 23.4 (Records).

**\[REQ-G-P26.0033\]: Individual Master Data Management and Traceability**

Requirement: The app shall manage Individual Master Data, including fields like \`ID/Fiscal/Tax Code\`, and support data acquisition by scanning physical documents (e.g., health insurance card / tessera sanitaria) for new patients. The system must restrict access to this data based on the operator's profile (e.g., Doctor, Assistant).

Rationale: Ensures correct identification and robust traceability of the individual (MDR Annex II, 1.1.d). Controlled access supports GSPR 17.2 and the requirements of ISO 13485:2016 (6.2).

**\[REQ-G-P26.0034\]: HL7 Standard Compliance for Data Exchange**

Requirement: The application's Server-side architecture shall support the utilization of the HL7 (Health Level Seven) standard for the transfer of clinical and administrative data to and from the Local App. A DTO translation layer must be implemented server-side to convert internal relational models to FHIR-compliant JSON payloads before transmission. 

Rationale: Demonstrates alignment with recognized international standards for healthcare data exchange, mitigating risks related to interoperability, security, and data integrity (MDR Annex I, GSPR 17).

**\[REQ-G-P26.0035\]: Cloud Synchronization and Local Storage Integrity**

Requirement: The DMA Local App must implement a secure, bi-directional data synchronization module with the Cloud Server and must be designed to allow for independent data acquisition and secure local storage when connectivity is unavailable. This process is managed locally via a local-DMA DB.

Rationale: Ensures data integrity and operational continuity in any environment (MDR Annex I, GSPR 17.1) and prevents the loss of critical patient data (ISO 13485:2016, 4.2.4).

## **7.2. DMA Device Data Stream Acquisition** {#7.2.-dma-device-data-stream-acquisition}

**\[REQ-G-P26.0036\] Serial Communication and Parsing**

Requirement: The system shall implement the SerialHandler module to manage low-level hardware communication. It must be able to send the command "go\\n" to trigger a reading and reliably read exactly 6 bytes from the serial buffer, correctly decoding and converting the data into a float format.

Rationale: The accuracy of the primary data is dependent on the correct and unambiguous reception of the 6-byte packet. Correct parsing is fundamental for scientific validity.

Verification Method:Functional I/O Serial Test; Validation of raw data integrity (6 bytes) against the final float value.

**\[REQ-G-P26.0037\] Linear Signal Transformation**

Requirement: The MeasurementEngine module shall compute the intermediate tension value (Y) by applying a linear transformation using the raw voltage, the Intercept (Y0), the Angular Coefficient (KK), and an Offset (S\_OFFSET), as defined in the configuration file.

Rationale: The calibration formula is the bridge between the raw electrical signal and the physical unit of measure. This calibration must be managed in a dedicated module and rigorously validated.

**\[REQ-G-P26.0038\] Final Current Calculation**

Requirement: The engine shall calculate the final current value (curr) by multiplying the Tension value (Y) by the active position multiplier and inverting the sign.

Rationale: The current value is the device's output data. Traceability and the correct application of the multiplier are essential for measurement reproducibility.

**\[REQ-G-P26.0039\] Skin Contact Detection**

Requirement: The MeasurementEngine must implement a pre-measurement logic that waits for a valid contact. This contact is confirmed when the raw voltage is less than or equal to the predefined limit (SKIN\_CONTACT\_LIMIT).

Rationale: Ensures that acquisition occurs only under correct operating conditions (probe in contact with the skin), preventing non-significant "open air" readings.

**\[REQ-G-P26.0040\] Saturation Monitoring and Flagging**

Requirement: During measurement, the software must compare the calculated current (curr) with the Upper/Lower saturation limits (e.g., POS\_1\_UP, POS\_1\_DOWN) mapped in the SAT\_LIMITS dictionary. If a limit is exceeded, an error flag (e.g., "SAT UP") must be appended to the data point and the outbound payload.

Rationale: Essential for Risk Management (ISO 14971). It immediately identifies readings exceeding the device's operating range, preventing invalid data.

**\[REQ-G-P26.0041\] Auto-Stop for Convergence Logic**

Requirement: If AutoStopMode is active, the engine shall successfully terminate the measurement loop if the relative variation between consecutive readings is less than or equal to the percentage tolerance (T\_VAR / 100\) for a strict number of consecutive iterations (NUM\_ITER).

Rationale: Automatic quality-of-measurement control. Ensures recording is completed only when the signal has stabilized to a reliable value.

**\[REQ-G-P26.0042\] Hardware Disconnection Handling**

Requirement: The system must actively monitor the hardware connection. If the SerialHandler returns the string value "DISCONNECTED" during position checks or data reads, the MeasurementEngine must immediately and safely abort the acquisition loop and report the error to the user interface.

Rationale: Crucial for safety and performance. Prevents erroneous or ambiguous readings caused by loss of connection and manages the error in a controlled manner (ISO 14971).

**\[REQ-G-P26.0043\] Position Change Management**

Requirement: The measurement engine shall continuously query the hardware for the physical switch position. If a change in position is detected during an active session, the engine must automatically reset the internal state (reset\_internal\_state) and discard all previously acquired session data.

Rationale: Guarantees data integrity. A measurement must be performed entirely with a single position multiplier. A variation invalidates the sequence, requiring a forced protocol restart. 

**\[REQ-G-P26.0068\] Software Safe-State Initialization**

Requirement: The software shall implement a "Safe-State" startup protocol.

Rationale: Ensures the device terminates immediately if critical parameters (config file) are missing or corrupted, preventing operation with unknown variables (MDR Annex I, 17.2).

**\[REQ-G-P26.0069\] \- Controlled Execution Environment**

Requirement: The application must support consistent execution across different deployment environments, specifically both as an interpreted Python script and as a compiled (frozen) binary executable. The software must implement dynamic path resolution logic to ensure that configuration files, logs, and assets are correctly identified regardless of the execution mode.

Rationale: This supports system reliability and software integrity as per MDR Annex I, GSPR 17.3, ensuring that the software behavior is predictable and that environmental setup errors do not lead to functional failures during clinical use.

**\[REQ-G-P26.0070\] \- Data Pipeline Integrity (Buffering)**

Requirement: The software shall implement a thread-safe, fixed-size data pipeline (buffer) for the transmission of electrical signals from the hardware acquisition engine to the external interfaces. The system must ensure that the sampling frequency is maintained and that no data packets are lost or corrupted during the internal transit between software threads.

Rationale: Required by MDR Annex I, GSPR 17.1 to ensure the accuracy and repeatability of the device's performance. Since DMA Screening relies on weak electrical signals, data integrity in the pipeline is critical for the generation of a valid metabolic profile.

**\[REQ-G-P26.0071\] \- External Interface & Network Control**

Requirement: The system must implement robust, thread-safe mechanisms to manage external client connections, dynamic operational state variables, and synchronous communication protocols to ensure real-time data flow reliability and controlled remote interaction.

Rationale: This is essential for maintaining the integrity and availability of the device's output data and ensuring control over the measurement workflow as required by MDR GSPR 17.3 (Software Integrity) and GSPR 17.1 (Performance).

### **7.2.1 System Orchestration and Core Control** {#7.2.1-system-orchestration-and-core-control}

**\[REQ-G-P26.0044\]: Global File-Based Logging System**

Requirement: The main application entry point shall initialize a globally accessible, file-based logging mechanism that forcefully removes any pre-existing handlers from the root logger. All log outputs must be directed exclusively to a file named DMA\_HardwareConnector.log, formatted to include the timestamp, severity level, logger name, and message content, operating at a DEBUG level. 

Rationale: Robust, file-based logging is a non-functional regulatory requirement for Post-Market Surveillance (PMS) and traceability. The log file serves as the definitive record of system operation, errors, and operator actions, necessary for auditability and compliance with ISO 13485:2016, 4.2.4 (Control of Records). Removing root handlers is a defensive measure to prevent output duplication.

**\[REQ-G-P26.0045\]: Configuration Load and Critical Error Control**

Requirement: The GenericUtils  module shall implement the load\_json\_config function to parse the init.json file. This function must handle path resolution with a fallback mechanism. Failure to locate the file after fallback attempts or encountering malformed JSON must result in logging a fatal error, printing a user-friendly message, and terminating the application immediately with exit code 1\. 

Rationale: Failure to load a critical configuration file must be treated as a fatal failure to prevent the device from operating with unknown or corrupted parameters. Immediate and controlled termination is essential for maintaining a safe state principle, addressing MDR Annex I, GSPR 17.2 (Error Handling) and 17.3 (System Integrity).

**\[REQ-G-P26.0046\]: Sequential Subsystem Initialization**

Requirement: The main  entry point shall orchestrate the sequential initialization of all subsystems: 1\) Load the global Config object. 2\) Initialize SerialHandler and attempt connection, terminating the application if an IOError is raised. 3\) Instantiate the ConnectionServer. 4\) Instantiate the MeasurementEngine, injecting the previously initialized objects.

Rationale: This ensures the correct dependency injection and operational sequence. The mandatory termination upon SerialHandler IOError confirms the device cannot proceed without a valid hardware connection, maintaining the safe state principle required by risk management (ISO 14971).

**\[REQ-G-P26.0047\]: Main Execution Loop Management**

Requirement: The application shall enter a polling loop, sleeping for the configured POLLING\_INTERVAL, until the ConnectionServer flags a request for a new reading (ReadingToStart) or a retake (MeasureRetake). While idle, it must continuously check for and apply dynamic updates to operational settings (autoStopMode and testMode) as communicated by the server. 

Rationale: Defines the central operating logic and state transition control. This mechanism ensures the device is consistently responsive to external commands from the UI/network client while maintaining a predictable, controlled execution environment, a core element of software validation.

### **7.2.2. Network Communication and Client Management** {#7.2.2.-network-communication-and-client-management}

**\[REQ-G-P26.0048\]: Asynchronous and Thread-Safe Concurrency**

Requirement: The ConnectionServer shall operate within a dedicated, isolated background thread, utilizing its own asynchronous event loop. This architecture must ensure that network Input/Output (I/O) operations do not block the main application thread, which is responsible for real-time hardware polling. 

Rationale: This is a critical architectural requirement for patient safety and performance (MDR Annex I, 17.1). It guarantees that real-time clinical data acquisition and processing remain uninterrupted by network latency or client communication, preventing an unacceptable delay or data loss during the measurement session.

**\[REQ-G-P26.0049\]: Robust Client Lifecycle and Keep-Alive**

Requirement: The server must actively track all connected WebSocket clients, automatically registering new connections and unregistering clients upon disconnection. It shall implement an asynchronous keep-alive mechanism that periodically sends a ping to each client. If a client fails to respond within a defined timeout, the system must forcibly disconnect and unregister that client to safely manage resources.

Rationale: Necessary for maintaining a stable and safe network environment (MDR Annex I, 17.1). This prevents resource exhaustion and ensures that dead or unresponsive connections do not interfere with the active measurement process, which is vital for system reliability.

**\[REQ-G-P26.0050\]: Measurement Data Buffering and Clearing**

Requirement: The ConnectionServer must provide a thread-safe mechanism (addMeasure) to store incoming measurement records in an internal buffer (self.measures). This buffer shall be strictly limited to a maximum size of 10 items, retaining only the most recently added measurements. Immediately after transmitting the buffer in a JSON response payload, the internal buffer must be cleared. 

Rationale: This defines a controlled, fixed-size data pipeline, essential for managing the flow of real-time data between the acquisition engine and the client UI. The size limit ensures the UI always receives the latest, relevant data points for visualization and prevents memory issues due to unconsumed data.

**\[REQ-G-P26.0051\]: Protocol Parsing and Measurement Control**

Requirement: The server must continuously receive and process incoming JSON-formatted messages, validating the protocol version. It shall decode the payload to update critical internal state flags (ReadingToStart, MeasureRetake, Reset) if present, thereby allowing the client to control the measurement lifecycle. The server shall then formulate a JSON response containing the protocol version, status code, current SwitchPosition, and the contents of the measurement buffer.

Rationale: This defines the Human-Machine Interface protocol, which is essential for the regulated control of the device by the operator. It ensures that commands from the UI are correctly interpreted and that the application status is reliably reported back to the operator for an informed medical procedure.

### **7.2.3 Utility & Configuration Functions** {#7.2.3-utility-&-configuration-functions}

**\[REQ-G-P26.0052\]: Path Resolution and Fallback Mechanism**

Requirement: The configuration loading module (GenericUtils) shall first attempt to locate the init.json file using the provided absolute or relative path. If the file is not found, the system shall not immediately fail but must attempt a fallback by constructing a new path using the current working directory (os.getcwd()) and must log a warning to notify the user of the path-switching strategy. 

Rationale: Ensures robustness in varied deployment environments (e.g., standard script execution vs. compiled/frozen executables like PyInstaller), preventing application failure due to minor environmental differences and improving system reliability (MDR Annex I, 17.3).

**\[REQ-G-P26.0053\]: Position Multiplier Mapping**

Requirement: The Config class must correctly read the individual position multiplier values (e.g., POS\_1, POS\_2, POS\_3) from the init.json file and restructure them into a single, accessible dictionary attribute (POSITIONS) keyed by integers (1, 2, 3\) for use by the MeasurementEngine.

Rationale: Proper and verifiable mapping of calibration coefficients (multipliers) to the measurement logic is critical for the accuracy and reproducibility of the device's output data, satisfying the performance requirements of MDR Annex I, GSPR 15\.

**\[REQ-G-P26.0054\]: Detachment Range Mapping**

Requirement: The Config  class shall accurately split the detachment\_range list (a two-element array) from the init.json into two distinct float attributes: DETACHMENT\_RAW\_MIN (index 0\) and DETACHMENT\_RAW\_MAX (index 1). \[cite: 1\]

Rationale: Ensures the MeasurementEngine correctly accesses the specific voltage thresholds required for the detachment state machine, which is necessary to control the measurement lifecycle and transition to the next state (MDR Annex I, 17.2).

## **7.3. DMA Sync Services Device (Edge) \- Cloud** {#7.3.-dma-sync-services-device-(edge)---cloud}

This subsection documents the requirements for the integrity, security, and resilience of the data synchronization module between the DMA Local App (Edge) and the Cloud Server, ensuring compliance with GSPR 17 (Data Security and Protection).

**\[REQ-G-P26.0055\]: Data Separation and Channel Protection**

Requirement: Sensitive Personal Data (PII, e.g., name, surname) must be transmitted via dedicated, separate channels from Operational Data (acquired measurements, logs). Operational data must be published through MQTT using pseudonymized identifiers.

Rationale: This separation reduces risk exposure, improves compliance with GDPR (data minimization and pseudonymization), and is a critical measure for data protection required by MDR Annex I, GSPR 17.2.

**\[REQ-G-P26.0056\]: End-to-End Encryption and Mutual Authentication**

Requirement: All data exchanges between the DMA Local App (Edge) and the Cloud Server must occur over TLS 1.3 with mutual authentication (mTLS). Device certificates or short-lived tokens must be used to identify each endpoint and enforce strict access control.

Rationale: Ensures end-to-end confidentiality and authenticity of the data, preventing interception and unauthorized injection of data packets. Essential for MDR Annex I, GSPR 17 (Confidentiality).

**\[REQ-G-P26.0057\]: Resilience and Offline Data Acquisition**

Requirement: The DMA Local App must enable data acquisition and logging independently from the status of the connectivity with the server. The application shall maintain a local queue for unsent records and implement an automatic retry mechanism when the network becomes available.

Rationale: Guarantees operational continuity in low-connectivity environments and ensures zero data loss, which is crucial for the reliability and safety of the device (MDR Annex I, GSPR 17.1).

**\[REQ-G-P26.0058\]: Unique ID and Integrity Management (UUID)**

Requirement: Core entities, including \`patients\` and \`visits\`, must use UUID v4 (Universally Unique Identifier) as the primary key. These UUIDs shall be generated locally by the App when operating offline to guarantee global uniqueness and prevent identifier conflicts during synchronization.

Rationale: Solves the critical challenge of key management in distributed, offline systems, ensuring data integrity and non-repudiation across the entire corpus (MDR Annex I, GSPR 17.1).

**\[REQ-G-P26.0059\]: Conflict Management Strategy (Optimistic Locking)**

Requirement: The Cloud Server MUST implement an Optimistic Locking strategy utilizing a version field for all synchronization records (BaseSyncEntity) to manage data conflicts (e.g., when two operators modify the same record). If a conflict occurs (HTTP 409 Conflict), the Local App MUST download the latest Server version and notify the operator (Merge UI).

Rationale: Prevents "lost updates" and ensures that the Server remains the ultimate "Source of Truth," maintaining transactional consistency across the distributed system (MDR Annex I, GSPR 17.1).

**\[REQ-G-P26.0060\]: Historical Data Management and Retention**

Requirement: Historical visit data must be loaded on-demand from the Cloud Server and shall NOT be kept long-term on the Local App. The Local App must enforce explicit auto-deletion of old decrypted history data upon reaching a configured local retention period (e.g., 10 days for visited patients).

Rationale: Minimizes local data exposure, reduces security risk, and improves compliance with the GDPR principle of data minimization, especially on mobile/edge devices (MDR Annex I, GSPR 17.2).

## **7.4. DMA Data Model Design &  Sync Services** {#7.4.-dma-data-model-design-&-sync-services}

This subsection documents the requirements for the central architecture, including the DMA Management Platform, the Global Domain, and the data model structure designed for regulatory compliance (GDPR, HIPAA) and data integrity (MDR Annex I, GSPR 17).

**\[REQ-G-P26.0061\]: DMA Management Platform Core Functionality**

Requirement: The central DMA Management Platform must expose services for the governance of the entire data lifecycle. This includes administrative management of entities (DMA Centers, DMA Devices, Contracts) and fine-grained flow control, such as the generation and approval of new protocols that are then deployed to the DMA Visit Apps in the appropriate domains.

Rationale: Ensures centralized control over the device's operational parameters and measurement protocols, satisfying the Quality Management System (QMS) requirement for controlled release of design output (ISO 13485:2016, 7.3.9).

**\[REQ-G-P26.0062\]: Domain and Global Segmentation (GDPR/Data Residency)**

Requirement: The architecture must be segmented into DMA Domains (geographic entities) that hold separate Domain Databases, with a central Global Domain where all data converges. The Domain Segmentation must be used to manage data residency according to different regional regulations (e.g., Europe vs. United States).

Rationale: Guarantees compliance with local data management criteria and data residency rules (e.g., GDPR), a fundamental requirement for MDR Annex I, GSPR 17.2. The segmentation also isolates operational issues.

**\[REQ-G-P26.0063\]: GDPR Right to Erasure (Art. 17\) \- Tombstone Pattern**

Requirement: The system MUST support the permanent deletion of patient data across all distributed nodes. Simple DELETE commands are prohibited. A "Tombstone" pattern must be implemented where deleted records are marked with is\_deleted \= true and deleted\_at timestamp to propagate the deletion to other clients and prevent "Zombie Data Resurrection".

Rationale: Explicitly addresses the GDPR Right to Erasure (Art. 17\) and ensures data integrity in the distributed system by maintaining a definitive record of deletion, essential for GSPR 17..

**\[REQ-G-P26.0064\]: GDPR Granular Consent (Art. 7\) Implementation**

Requirement: The data model MUST incorporate explicit boolean fields for Granular Consent on the User/Patient entity, including a minimum of consent\_data\_processing (required for basic medical processing), consent\_research, and consent\_marketing.

Rationale: Ensures strict compliance with GDPR Art. 7, moving beyond a monolithic consent structure to uphold the principle of Privacy by Design and supporting GSPR 17.2.

**\[REQ-G-P26.0065\]: Audit Logs and Traceability**

Requirement: A dedicated Log Database (Log DB) must be maintained, separate from the primary data, to monitor system activities, including system accesses (successful/failed), failed transactions, anomalies, and potential malware threats. This is to ensure a constant trace of operations performed on the data.

Rationale: Ensures security, data protection, and service continuity, and is explicitly required by GDPR and for forensic analysis and accountability (Who changed what and when), supporting MDR Annex I, GSPR 17\.

**\[REQ-G-P26.0066\]: Data Retention Policy Implementation**

Requirement: The Cloud Server MUST automatically enforce the data lifecycle according to the defined policy: Clinical Data retained for 10 Years from the last visit (or per local medical law) and Audit Logs retained for 6 Years (HIPAA standard).

Rationale: Ensures compliance with both medical law and security regulations, adhering to the data minimization principle (GDPR Art. 5(1)(e)) and supporting MDR Annex I, GSPR 17\.

**\[REQ-G-P26.0067\]**: **Physical Separation of Application and Database Servers**

Requirement: The Cloud Server architecture MUST implement the physical separation of Database (DB) components (including the Domain DBs and the Global DB) from the Application Servers (which execute business logic and APIs). The database components must reside on distinct infrastructural hosts or services dedicated exclusively to data management and storage.

Rationale: This separation implements a defense-in-depth principle, reducing the attack surface and limiting the impact of a potential breach at the application server level. This is fundamental for guaranteeing data confidentiality and integrity, in line with the principles of MDR Annex I, GSPR 17.2.

**\[REQ-G-P26.0081\]: Multilingual Support Schema**

Requirement: The DMA system shall support at minimum Italian and English languages for all user-facing content. The data model shall provide a multilingual sub-schema to manage textual content translations centrally.

Rationale: Enables scalability as the system grows.

**\[REQ-G-P26.0082\]: Metabolic Pathway Integration Schema**

Requirement: The Protocol entity shall support optional association with externally catalogued Metabolic Pathways (Reactome, KEGG) to enable biologically-informed protocol documentation and future AI-driven enrichment.

Rationale: Enables standards for future research.

## **7.5. DMA Algorithms** {#7.5.-dma-algorithms}

**\[REQ-G-P26.0072\]: External Algorithm Configuration Management**

Requirement: The DMA Algorithms component shall load all processing parameters at runtime from an external XML configuration file (config.xml), including: input/output file paths, eight numerical processing thresholds, and output file label strings. No parameter shall be hardcoded in the processing scripts. Failure to locate or parse the configuration file shall result in a controlled error with a user-facing message.

Rationale: Externalising configuration enables threshold tuning for different clinical protocols without modifying or redeploying the algorithm code, supporting maintainability and reducing the risk of uncontrolled software changes (ISO 13485:2016 Clause 7.3.7).

**\[REQ-G-P26.0018\]: Data Analysis Computation**

Requirement:The software shall calculate Patient Derived Indices (e.g., Total Emission Variability) and utilize mathematical modules to generate a descriptive report that provides non-clinical interpretive indications related to well-being, in line with the official Intended Purpose of the device.

Rationale:Satisfies the intended purpose of the device: to provide auxiliary information about metabolic processes. The use of validated algorithms is a Performance requirement (MDR Annex I, 15).

### **7.5.1. Basal Analysis Algorithms**

**\[REQ-G-P26.0087\]: Basal Emission Analysis and Aggregation**

Requirement: The Basal Analysis Algorithms shall compute and aggregate overall bioelectrical body emission indicators, including total, average, variance, and median across all measured points, and generate specific symmetric/asymmetric indicators across body regions (e.g., left vs. right, upper vs. lower, hands vs. feet) and point-level asymmetry.

Rationale: Essential for providing a comprehensive initial view of the body's bioelectrical state and identifying key indicators of body emission and asymmetry during the Basal Analysis.

**\[REQ-G-P26.0088\]: Relational Emission Comparison Matrices**

Requirement: The Basal Analysis Algorithms shall generate comparison matrices for both Point-to-Point and District-to-District basal emissions. These matrices must calculate absolute, percentage, and logarithmic differences, and apply clustering techniques (e.g., standard ranges, quartiles) to highlight significant emission variations.

Rationale: Provides detailed relational insight into metabolic processes by comparing points and districts, a key part of the device's intended purpose to deliver non-clinical interpretive indications.

**\[REQ-G-P26.0089\]: Data Significance, Mapping, and Export for Basal Analysis**

Requirement: The system shall compute significance of Basal Emission values against physiological bounds, identifying and statistically analyzing unreliable data. It must map reliable basal emission values to predefined reference ranges (e.g., hyper/hypo states) and ensure all resulting calculations, matrices, and indicators are structured and exported into a format suitable for storage and external consumption (e.g., JSON).

Rationale: Ensures the integrity and significance of the calculated data and provides a standardized, exportable output structure for downstream processing and report generation.

## 

## **7.6. Report Generation & Signature Requirements** {#7.6.-report-generation-&-signature-requirements}

**\[REQ-G-P26.0029\]: Data Analysis to support  Report Generation**

Requirement: The software shall calculate Patient Derived Indices and utilize mathematical modules to generate a descriptive report that provides non-clinical interpretive indications. Rationale: Satisfies the intended purpose (GSPR 15). The operator's digital signature ensures the attribution, accountability, and integrity of the clinical output (GSPR 16).

**\[REQ-G-P26.0083\]: Structured Data Model for Visit State**

Requirement: The software system shall define and utilize standardized, structured data objects (e.g., Python dataclasses) to represent the entire state of the visit, including patient metadata, raw results, algorithmic outputs, and structured manual operator inputs, ensuring seamless data flow between all report generation sub-modules.

Rationale: Ensures data consistency, type safety, and traceability across the complex, multi-stage report generation pipeline, supporting software integrity (MDR Annex I, GSPR 17.3).

**\[REQ-G-P26.0084\]: Controlled Data Ingestion and Input Retrieval**

Requirement: The Report Generation module shall implement controlled, dedicated mechanisms for importing all necessary data inputs, including fixed, multilingual reference data (default tables/phrases) and dynamically retrieved patient-specific clinical data (algorithmic results, master records, anamnesis).

Rationale: Ensures that all necessary static and dynamic information is accurately sourced for the report, providing the foundation for content generation and meeting traceability requirements.

**\[REQ-G-P26.0085\]: Content Generation and Enforcement Logic**

Requirement: The software shall implement a robust processing logic to extract data from the structured data model, evaluate specific clinical conditions (e.g., marker activation, mutual phrases/enforcement logic), and map these results to predefined, controlled text blocks and sections for report content assembly.

Rationale: Ensures the correct and context-aware generation of the descriptive, non-diagnostic content in the report, maintaining compliance with the device's intended purpose (MDR Annex I, GSPR 16).

**\[REQ-G-P26.0086\]: Final Report Formatting and Output Integrity**

Requirement: The system shall utilize programmatic templating and formatting engines (e.g., HTML/CSS, LaTeX, Typst via Python) to assemble the final report document, strictly enforcing all defined layout, styling, and structural constraints to ensure a consistent, auditable, and regulatory-compliant final output.

Rationale: Guarantees the professional and legally required presentation of the final medical device output, ensuring data clarity and consistency across all generated documents (MDR Annex I, GSPR 14).

8. # **Cybersecurity General Requirements** {#cybersecurity-general-requirements}

**\[REQ-G-P26.0073\] Data Encryption at Rest (Local & Cloud)**

Requirement: All sensitive data, including raw bioelectrical signals and patient metadata, must be encrypted when stored in the Local Offline Database and the Cloud Database using industry-standard encryption protocols (e.g., AES-256).

Rationale: To ensure confidentiality and comply with GDPR/MDR requirements regarding the protection of sensitive health data against unauthorized physical or digital access.

**\[REQ-G-P26.0074\] Secure Data Synchronization (In-Transit)**

Requirement: Data transmission between the Edge Layer (Visit App) and the Cloud Infrastructure must occur via secure, encrypted channels (e.g., TLS 1.3 or higher) with mutual authentication.

Rationale: To prevent "Man-in-the-Middle" (MitM) attacks and ensure the integrity of raw data during the synchronization process from the clinician's PC to the processing server.

**\[REQ-G-P26.0075\] User Authentication & Role-Based Access Control (RBAC)**

Requirement: Access to the Visit App and Cloud Dashboard must be restricted to authorized personnel via strong authentication mechanisms (MFA recommended). The system must enforce RBAC to limit data access based on the user's role (e.g., Clinician, Admin).

Rationale: To prevent unauthorized clinical use and ensure that only trained operators can initiate protocols or view metabolic reports, as per ISO 13485:2016 (7.3.3).

**\[REQ-G-P26.0076\] Data Integrity & Audit Logging**

Requirement: The system must maintain an immutable audit log of all critical operations, including data acquisition, synchronization, algorithmic processing, and report generation. Any modification to data must be detectable.

Rationale: Essential for "Traceability by Design." It ensures the medical output is immutable and provides a forensic trail in case of performance anomalies or security breaches (MDR Annex I, 17.4).

**\[REQ-G-P26.0077\] Cloud Infrastructure Resilience & Hardening**

Requirement: The Cloud environment hosting the algorithms and databases must implement security hardening, including firewalls, intrusion detection systems (IDS), and regular vulnerability scanning.

Rationale: To protect the core processing engine (Algorithms) from external threats that could alter metabolic indicators or cause service downtime.

**\[REQ-G-P26.0078\] Software Integrity & Secure Updates**

Requirement: The system must verify the integrity of software components (Edge and Cloud) before execution. Updates to the Visit App or Cloud-side algorithms must be delivered through secure, signed packages.

Rationale: To ensure that the validated version of the algorithm (deterministic or ML-based) is the one actually performing the assessment, preventing code injection or unauthorized modifications.

**\[REQ-G-P26.0079\] Report Integrity and Electronic Signatures**

Requirement: The generated report template must be protected against post-generation alteration. The system must support electronic signatures to link the output to the responsible clinician.

Rationale: To satisfy MDR requirements for technical documentation and medical records, ensuring that the descriptive metabolic indicators remain accurate throughout the professional review process.

**\[REQ-G-P26.0080\] External Penetration Testing**

Requirement: The system's security, including the Visit App and Cloud Infrastructure, must be assessed through a formal penetration test (Pentest) conducted by an independent, external security company.

Rationale: To objectively validate the effectiveness of all implemented security controls (e.g., encryption, RBAC, hardening) and ensure compliance with the essential security requirements for medical device software (e.g., MDCG 2019-16).

9. # **Document Governance** {#document-governance}

   1. ## **Revision List & Notes**  {#revision-list-&-notes}

| Revisision  | Date | Approved By \-  Name Acronymus | Notes |
| :---- | :---- | :---- | :---- |
| 00.02 |  |  |  |
| 00.01 |  |  |  |
| 00.00 | 2026m04d07 | \[GB\] | First edition |

   2. **Authors, Contributors & Reviewers** 

| Name & Surname  \[Name Acronymus\] | Role:  \[Authors, Contributors, Reviewers, Approver\] |
| :---- | :---- |
| Giampiero Bartolomei \[GB\] |  Author; Approver |
|  |  |
|  |  |

   3. **Approvals**

| Date | Name & Surname   | Role | Signature |
| :---- | :---- | :---- | :---- |
| yyyymMMdDD |  |  |  |
|  |  |  |  |
|  |  |  |  |

