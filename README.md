# Clinical Workflow Signal Audit

> **Status:** Case Study  Synthetic Healthcare Workflow Backend

A synthetic ICU workflow audit backend for tracking signal-to-action latency, escalation states, data quality, and operational workflow visibility.

The project uses deterministic workflow logic and a FHIR R4 interoperability layer to represent workflow events as structured healthcare resources. It is designed for workflow analytics and auditability, not diagnosis or autonomous clinical decision-making.

---

## Live Portfolio Case Study

View the published case study:

https://workflow-signal-audit.lovable.app

---

## Overview

ICU workflows receive signals from multiple sources, including bedside monitoring, laboratory systems, EMR documentation, alarms, handoffs, and other operational records.

When these signals are fragmented, it becomes difficult to reconstruct:

- What happened
- When it happened
- Whether the data was reliable
- What workflow tier was assigned
- Whether the expected action occurred
- How long the signal took to move through the workflow

**Clinical Workflow Signal Audit** models this problem using synthetic data.

The backend converts workflow events into structured representations for:

- Signal-to-action audit trails
- Data quality checks
- Workflow risk tiers
- Escalation state tracking
- SLA and latency analysis
- FHIR-based interoperability
- Human review and workflow feedback

This is **not a diagnostic AI system** and does not make autonomous clinical decisions.

---

## What This Project Demonstrates

This project demonstrates:

- FastAPI backend development
- Synthetic healthcare workflow data
- Deterministic workflow and escalation logic
- Signal-to-action latency modelling
- Data quality and uncertainty handling
- FHIR R4 resource modelling
- API design for Patient, Observation, and Task resources
- FHIR Bundle construction
- Custom FHIR CodeSystems
- Automated unit testing
- HAPI FHIR validation
- Healthcare AI safety and human-in-the-loop design

---

## Architecture

``text
Synthetic ICU Workflow Events
          |
          v
   Workflow Audit Model
          |
          +-- Data Quality
          |
          +-- Signal-to-Action Latency
          |
          +-- Workflow Risk Tier
          |
          +-- Escalation State
          |
          v
   Deterministic Workflow Logic
          |
          v
   FHIR Interoperability Layer
          |
          +-- Patient
          +-- Observation
          +-- Task
          |
          v
        Bundle
          |
          v
   FastAPI /fhir API
          |
          v
   Tests + FHIR Validation
```text

### Architectural Boundary

FHIR is used as a **representation and interoperability layer**.

The project's workflow rules remain deterministic and testable. Critical workflow decisions are not delegated to an LLM.

This separation keeps:

* Workflow logic deterministic
* Interoperability standards-based
* AI usage constrained
* Clinical uncertainty explicit
* Testing reproducible

---

## Core Workflow

```text
Workflow Event


Signal Generated


Signal Detected


Workflow Tier
Monitor | Review | Escalate | Activate


Escalation State
Pending  Acknowledged  Completed


Action Timestamps


Signal-to-Action Audit
```

The FHIR layer represents these operational events without inventing clinical measurements that are not present in the source dataset.

---

# FHIR Interoperability

The project includes a FHIR R4 interoperability layer for representing synthetic workflow events.

The current implementation models:

| Resource      | Purpose                                                         |
| ------------- | --------------------------------------------------------------- |
| `Patient`     | Represents the synthetic workflow subject                       |
| `Observation` | Represents a workflow signal and its timing                     |
| `Task`        | Represents operational workflow work associated with the signal |
| `Bundle`      | Packages the related Patient, Observation, and Task resources   |

### Validation Status

The FHIR resources have been validated using the HAPI FHIR validator against FHIR version **4.0.1**.

```text
FHIR Version:       4.0.1
HAPI Validator:     6.10.4
Patient:            PASS
Observation:        PASS
Task:               PASS
Bundle:             PASS
Validation Errors:  0
```

The validator still reports informational warnings and notes for some best-practice or terminology details. These are retained rather than being hidden by fabricating clinical metadata.

> **Important:** This project does not claim to implement a complete production FHIR server or universal FHIR conformance.

---

## Observation Resource

The Observation layer maps supported workflow signal types to standard LOINC codes where applicable.

Current mappings include:

| Signal           | LOINC    |
| ---------------- | -------- |
| Heart Rate       | `8867-4` |
| Respiratory Rate | `9279-1` |
| Body Temperature | `8310-5` |

The source synthetic dataset does **not** contain actual measurement values.

The implementation therefore does not invent values.

Instead, unsupported measurements are represented using:

```text
dataAbsentReason = unsupported
```

This preserves the distinction between:

1. A measurement that actually exists
2. A measurement that is missing
3. A measurement that was never available in the source dataset

---

## Task Resource

FHIR `Task` resources represent operational workflow work associated with a signal.

Task status is derived deterministically from the source escalation state and action timestamps.

The implementation maps workflow state into FHIR Task status without pretending that project-specific workflow concepts are native FHIR clinical priorities.

For example:

```text
Pending + no action timestamps

FHIR Task: requested
```

```text
Acknowledged + no action start

FHIR Task: accepted
```

```text
Acknowledged + action started

FHIR Task: in-progress
```

```text
Completed + completion timestamp

FHIR Task: completed
```

Invalid combinations are rejected rather than silently converted.

The implementation deliberately does **not**:

* Map workflow tiers directly to FHIR `priority`
* Map SLA breaches to FHIR `failed`
* Invent owners or requesters
* Invent clinical orders
* Invent clinical measurements

The Task resource instead preserves the project's operational workflow semantics through explicit custom terminology.

---

## FHIR Bundle

The workflow Bundle packages the related:

```text
Patient

    Observation

    Task
```

The Bundle uses canonical resource references so that relationships between resources remain explicit.

The generated Bundle represents a single synthetic workflow event as a collection of related FHIR resources.

---

## Custom CodeSystems

The repository includes project-specific CodeSystems for concepts that are not represented directly by standard terminology.

Current CodeSystems include:

```text
record-kind
signal-type
escalation-state
workflow-tier
```

These allow the application to preserve project-specific workflow semantics while keeping the FHIR resource structures explicit.

---

# API

The project uses **FastAPI** for the backend API.

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

---

## Patient

Create a synthetic Patient resource:

```http
POST /fhir/Patient
```

Retrieve a Patient:

```http
GET /fhir/Patient/{patient_id}
```

---

## Observation

Create an Observation:

```http
POST /fhir/Observation
```

Retrieve an Observation:

```http
GET /fhir/Observation/{observation_id}
```

---

## Task

Create a Task:

```http
POST /fhir/Task
```

Retrieve a Task:

```http
GET /fhir/Task/{task_id}
```

---

## Endpoint Summary

```text
GET  /health

POST /fhir/Patient
GET  /fhir/Patient/{patient_id}

POST /fhir/Observation
GET  /fhir/Observation/{observation_id}

POST /fhir/Task
GET  /fhir/Task/{task_id}
```

These endpoints provide lightweight resource storage for the project demonstration.

They are **not intended to represent a complete production FHIR server**.

---

# Workflow Risk Tiers

The workflow layer uses four operational risk tiers:

| Tier     | Meaning                          | Expected Workflow                          |
| -------- | -------------------------------- | ------------------------------------------ |
| Monitor  | No immediate workflow risk       | Continue routine observation               |
| Review   | Signal requires review           | Nurse review within 30 minutes             |
| Escalate | Signal requires clinician action | Clinician review within 15 minutes         |
| Activate | Critical workflow risk           | Highest-priority response within 5 minutes |

These are **operational workflow categories**, not clinical diagnoses.

The project uses the tiers to model how workflow state can affect routing, review, and escalation.

---

# Escalation State Machine

The workflow uses an explicit state model:

```text
Pending


Acknowledged


Action Initiated


Completed
```

Workflow timestamps allow the system to calculate signal-to-action latency and determine whether the expected workflow occurred within the configured SLA.

The implementation validates state/timestamp combinations rather than silently accepting inconsistent records.

---

# Deterministic Task IDs

Task IDs are generated deterministically from the source event identifier using UUIDv5.

This provides stable identifiers for the same synthetic event across repeated generation.

Conceptually:

```text
event_id

UUIDv5

FHIR Task.id
```

This helps make generated resources reproducible and easier to test.

---

# Data Handling

This project uses **synthetic data only**.

No real patient records, protected health information, hospital identifiers, or private clinical data are included.

The source dataset does not contain clinical measurement values for the FHIR Observation resources.

The implementation intentionally avoids inventing those values.

---

# Responsible AI Positioning

This project does not diagnose patients or replace clinicians.

The workflow layer is designed to make operational state explicit.

It focuses on questions such as:

* What signal was generated?
* When was it detected?
* What workflow tier was assigned?
* What escalation state was reached?
* When did action begin?
* When was action completed?
* Was the SLA met?
* Was the available data sufficient to represent the event?

Where uncertainty or missing information exists, the implementation preserves that limitation rather than manufacturing a value.

### Human-in-the-Loop

The system is designed around human review rather than autonomous clinical action.

The architecture intentionally separates:

```text
Data

Deterministic Workflow Logic

Operational State

Human Review / Action
```

AI should not be treated as the authority for critical clinical decisions.

---

# Testing

The repository includes automated tests covering:

* Patient resource construction
* Observation resource construction
* LOINC mappings
* Timestamp handling
* Synthetic event loading
* Task status derivation
* Task execution periods
* Deterministic Task IDs
* API resource creation and retrieval
* Workflow Bundle relationships
* Cross-resource FHIR references
* Invalid state/timestamp combinations
* Synthetic event conversion

## Current Test Result

```text
46 passed
1 warning
```

The warning is a Starlette/httpx deprecation warning from the test client dependency and is unrelated to test failures.

Run the test suite with:

```powershell
python -m pytest -q
```

---

# FHIR Validation

The repository includes a repeatable validation workflow using the HAPI FHIR validator.

Run:

```powershell
.\scripts\validate_fhir.ps1
```

The validation workflow checks generated:

```text
Patient
Observation
Task
Bundle
```

resources against FHIR R4 / version 4.0.1.

### Latest Validation Result

```text
FHIR Version:       4.0.1
HAPI Validator:     6.10.4

Patient       PASS
Observation   PASS
Task          PASS
Bundle        PASS

Errors: 0
```

Validation artifacts are stored under:

```text
validation/
```

The repository intentionally retains informational validator warnings and notes rather than modifying the resources solely to suppress them.

---

# Project Structure

```text
clinical-workflow-signal-audit/

 README.md

 app/
    __init__.py

    fhir/
       __init__.py
       observation.py
       patient.py
       routes.py
       synthetic_events.py
       task.py
       workflow_bundle.py

    main.py

 data/
    generated/
        synthetic_icu_workflow.csv

 docs/
    case_study.md
    dashboard_spec.md
    risk_tiering_logic.md
    responsible_ai.md

 scripts/
    generate_fhir_validation_samples.py
    validate_fhir.ps1

 sql/
    postgres_schema.sql

 tests/
    test_observation.py
    test_patient.py
    test_synthetic_events.py
    test_task.py
    test_workflow_bundle.py

 validation/
    Bundle-validation.json
    Observation-validation.json
    Patient-validation.json
    Task-validation.json
    codesystems/
        CodeSystem-escalation-state.json
        CodeSystem-record-kind.json
        CodeSystem-signal-type.json
        CodeSystem-workflow-tier.json

 ...
```

---

# Engineering Boundaries

The project intentionally separates four concerns.

## 1. Workflow Logic

Deterministic rules handle:

* Workflow tiers
* Escalation states
* Timestamp relationships
* Task status
* Signal-to-action latency

---

## 2. Interoperability

FHIR resources provide a structured representation of:

* Patients
* Workflow observations
* Operational tasks
* Relationships between resources

FHIR is not being used as the workflow engine.

---

## 3. AI

AI is not used to make autonomous critical clinical decisions.

The architecture preserves:

* Human review
* Explicit uncertainty
* Deterministic state transitions
* Testable workflow rules

---

## 4. Synthetic Data

The demonstration uses synthetic healthcare workflow events so that the system can be developed and validated without exposing real patient information.

---

# Running Locally

## 1. Clone the Repository

```powershell
git clone https://github.com/arapkirui513-hub/clinical-workflow-signal-audit.git
cd clinical-workflow-signal-audit
```

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the following in the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Run Tests

```powershell
python -m pytest -q
```

## 5. Start the API

```powershell
uvicorn app.main:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Validation Workflow

A complete local verification can be performed with:

```powershell
python -m pytest -q
.\scripts\validate_fhir.ps1
```

Expected results:

```text
Tests:
46 passed

FHIR:
Patient       PASS
Observation   PASS
Task          PASS
Bundle        PASS
Errors:       0
```

---

# Portfolio Context

This repository provides the technical implementation behind the public Clinical Workflow Signal Audit case study.

It demonstrates the progression from:

```text
Healthcare Workflow Problem

Synthetic Event Model

Deterministic Workflow Logic

API Representation

FHIR Interoperability

Automated Testing

External Validation

Portfolio Case Study
```

The project is intended to demonstrate practical engineering around healthcare workflows, interoperability, data quality, and responsible AI boundaries.

---

# Key Engineering Decisions

### No fabricated clinical measurements

The source dataset does not contain actual measurement values, so the FHIR Observation layer does not invent them.

### Deterministic workflow state

Workflow and escalation transitions are represented using explicit rules rather than opaque model output.

### FHIR as an interoperability layer

FHIR provides standardized resource representation without replacing the project's workflow engine.

### Explicit uncertainty

Missing or unsupported information is represented explicitly rather than silently filled.

### Human oversight

The architecture supports human review and does not position AI as an autonomous clinical decision-maker.

### Validation before claims

FHIR resources are validated with an external HAPI FHIR validator before making interoperability claims.

---

# Limitations

This is a portfolio and engineering demonstration, not a production clinical system.

It does not currently provide:

* A production-grade FHIR server
* Authentication and authorization
* Multi-user persistence
* Hospital-system integration
* Real-time device ingestion
* Real patient data
* Clinical decision support
* Clinical diagnosis
* Production-grade audit/security controls
* Full FHIR conformance across all resource profiles and workflows

These limitations are intentional and define the scope of the project.

---

# Future Extensions

Potential future engineering work could include:

* PostgreSQL-backed FHIR resource persistence
* FHIR search parameters
* Resource versioning
* Authentication and authorization
* SMART on FHIR integration
* Broader terminology validation
* Additional FHIR resources
* Real-time event ingestion
* More comprehensive interoperability testing
* Production-grade audit logging
* Role-based access control

These would be extensions of the current demonstration rather than assumptions about existing functionality.

---

# Repository

GitHub:

[https://github.com/arapkirui513-hub/clinical-workflow-signal-audit](https://github.com/arapkirui513-hub/clinical-workflow-signal-audit)

Live case study:

[https://workflow-signal-audit.lovable.app](https://workflow-signal-audit.lovable.app)

---

## License

This repository is a portfolio engineering project using synthetic healthcare workflow data.

````
