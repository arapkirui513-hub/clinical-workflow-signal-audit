# Clinical Workflow Signal Audit

Healthcare workflow intelligence demo for auditing ICU signal-to-action latency, escalation SLAs, data quality gaps, and role-based dashboard logic using synthetic data.

## Live Portfolio Case Study

View the published case study here:

https://workflow-signal-audit.lovable.app

## Overview

ICU teams receive signals from bedside monitors, lab systems, EMR notes, ventilators, alarms, handoffs, and clinician assessments. These signals often sit across fragmented systems, causing delayed escalation, missed trends, incomplete documentation, and poor visibility during shift changes.

Clinical Workflow Signal Audit shows how fragmented ICU signals can be converted into:

- A signal-to-action audit trail
- Data quality checks
- Action-driven workflow tiers
- SLA-based escalation routing
- A role-based dashboard for operations visibility
- A human override and feedback loop

This is not a diagnostic AI tool. It is a workflow intelligence layer for tracking operational risk and escalation latency.

## What this project demonstrates

- Clinical workflow mapping
- Synthetic healthcare data generation
- Data quality validation
- Signal-to-action latency tracking
- PostgreSQL schema design
- Model-agnostic output structure
- Dashboard UX design
- Healthcare AI product positioning

## Project structure

```text
clinical-workflow-signal-audit/
│
├── README.md
├── data/
│   └── synthetic_data_placeholder.md
│
├── scripts/
│   └── deepseek_python.py
│
├── sql/
│   └── postgres_schema.sql
│
├── docs/
│   ├── case_study.md
│   ├── dashboard_spec.md
│   ├── risk_tiering_logic.md
│   └── responsible_ai.md
│
└── assets/
    ├── screenshots/
    │   ├── dashboard_overview.png
    │   ├── high_risk_queue_ai_action.png
    │   ├── escalation_sla_tracker.png
    │   └── data_quality_monitoring.png
    │
    └── video/
        └── signal_audit_visual_explainer.mp4
```

## Core workflow

```text
Data Sources
Vitals | Labs | EMR Notes | Alarms | Handoffs | Ventilator Data

        ↓

Signal Audit Trail
Generated → Detected → Acknowledged → Action Initiated → Action Completed

        ↓

Data Quality Layer
Missing values | Backdated vitals | Clock drift | Impossible values | Incomplete notes

        ↓

Workflow Risk Layer
Monitor | Review | Escalate | Activate

        ↓

Escalation State Machine
Pending → Acknowledged → Action Initiated → Completed
       ↘ SLA Breached → Auto-escalate

        ↓

Dashboard Layer
Patient queue | SLA tracker | Lab delays | Documentation gaps | Recommended actions
```

## Workflow risk tiers

| Tier | Meaning | Expected action |
|---|---|---|
| Monitor | No immediate workflow risk | Continue routine observation |
| Review | Signal needs nurse review | Nurse assessment within 30 minutes |
| Escalate | Signal needs clinician action | Resident or order review within 15 minutes |
| Activate | Critical workflow risk | RRT or attending response within 5 minutes |

## Dashboard views

The dashboard prototype includes:

- Operations overview
- High-risk patient queue
- AI recommended workflow action
- Escalation SLA tracker
- Lab delay and data quality monitoring
- Score suppression for unreliable data
- Human-in-the-loop override controls

## Data handling

This project uses synthetic data only.

No real patient records, protected health information, hospital identifiers, or private clinical data are included.

## Responsible AI positioning

This project does not diagnose patients or replace clinicians.

It supports workflow visibility by answering:

- Which signal needs action?
- Who should act?
- How fast should they act?
- Was the SLA met?
- Where did the signal stall?
- Was the data reliable enough to route?

## Portfolio use

Use this repository as the technical proof behind the public case study.

Suggested links:

- Portfolio page: add your Lovable URL
- Notion case study: add your public Notion URL
- LinkedIn post: add your launch post URL
