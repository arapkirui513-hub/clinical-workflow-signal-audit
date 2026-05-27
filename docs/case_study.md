# Clinical Workflow Signal Audit

## A workflow intelligence demo for reducing ICU escalation delays caused by fragmented clinical signals

**Project type:** Healthcare AI workflow intelligence demo  
**Focus area:** ICU escalation delays and signal-to-action latency  
**Role:** Workflow designer, data pipeline builder, AI systems planner, dashboard UX designer  
**Status:** Portfolio demo using synthetic data only  
**Primary audience:** Hospital operations teams, nurse managers, healthtech founders, and healthcare AI product teams  

---

## 1. Executive Summary

ICU teams work in high-pressure environments where patient signals come from many places at once: bedside monitors, lab systems, EMR notes, ventilators, alarms, handoffs, and clinician assessments.

The problem is not only that data exists in silos. The larger problem is **signal-to-action latency**.

A warning signal may exist, but the right person may not see it, acknowledge it, route it, act on it, or complete the intervention in time.

**Clinical Workflow Signal Audit** is a portfolio demo that shows how fragmented ICU signals can become a structured workflow intelligence layer.

The system tracks each signal from generation to completed action, checks data quality, assigns workflow risk tiers, monitors escalation SLAs, and presents the status in a role-based dashboard.

This is not a diagnostic AI tool. It does not tell clinicians what disease a patient has. It helps teams see where operational risk is building and where escalation workflows are stalling.

---

## 2. The Problem

ICU deterioration signals are generated continuously, but they often move through fragmented systems.

Vitals may sit in bedside monitors. Lab results may arrive asynchronously. Documentation may lag behind real-time events. Escalation may happen through pager, phone, verbal handoff, or EMR alert. During a busy shift, this creates gaps between when a signal exists and when action happens.

### Core workflow breakdowns

- Vitals, labs, notes, alarms, and handoffs live in separate systems.
- Staff must manually reconstruct patient trajectory from scattered views.
- Documentation can happen after the clinical event, which makes the EMR look cleaner than the real workflow.
- Handoff summaries can lose subtle trends.
- Pager-based communication may lack read receipts or auditability.
- Nurse managers and operations teams struggle to see exactly where escalation delays happen.
- Data quality issues such as missing labs, backdated vitals, impossible values, and clock drift can distort risk scoring.

### Product framing

The project frames the ICU challenge as a **signal-to-action latency problem**:

> How long does it take for a patient signal to move from generation to detection, acknowledgment, action initiation, and completed intervention?

---

## 3. Fictional ICU Scenario

A patient in Bed 12 develops rising lactate, worsening tachycardia, and delayed documentation over a four-hour period.

The signals exist, but they are fragmented:

- The lactate trend appears in the lab system.
- Heart rate changes appear on the bedside monitor.
- Nursing notes are updated later.
- The resident has not acknowledged the alert.
- The attending sees the full patient trajectory only after escalation is already delayed.

In the current workflow, the team has to reconstruct the full picture manually.

With Signal Audit, the same four-hour period becomes visible as a timeline:

1. Signal generated  
2. Signal detected  
3. Signal acknowledged  
4. Action initiated  
5. Action completed  
6. SLA status recorded  
7. Data quality issues flagged  
8. Override or feedback captured  

The system helps answer practical workflow questions:

- What changed?
- When did it change?
- Who saw it?
- Who acknowledged it?
- What action happened?
- Was the SLA met?
- Was the data reliable?
- Where did the signal stall?

---

## 4. Project Goal

The goal was to build a synthetic workflow intelligence demo that shows how fragmented ICU data can become clear escalation pathways.

### The system needed to:

- Track signal generation, detection, acknowledgment, action initiation, and action completion.
- Flag missing, delayed, backdated, or unreliable data.
- Convert raw signals into action-driven workflow tiers.
- Track SLA breaches and routing attempts.
- Show managers and clinicians where signals are stalling.
- Support human override and auditability.
- Separate workflow intelligence from clinical diagnosis.

---

## 5. What I Built

### 5.1 Synthetic ICU Workflow Dataset

I created a synthetic dataset representing ICU signal flow, patient risk context, workflow timing, escalation status, and data quality issues.

The dataset simulates:

- Patient vitals
- Lab delay
- Alert timing
- Acknowledgment timing
- Escalation timing
- Action completion
- Documentation quality
- Shift context
- Signal source visibility
- Workflow bottlenecks
- Risk tiering
- SLA status

The dataset is synthetic and designed for product demonstration only.

---

### 5.2 Python Data Pipeline

The Python pipeline supports:

- Synthetic data generation
- Data quality checks
- Cleaning rules
- Workflow latency calculations
- Risk tier assignment
- Bottleneck analysis
- Portfolio-ready summary metrics

The pipeline focuses on workflow events rather than diagnosis.

Example latency fields:

- `signal_generated_time`
- `signal_detected_time`
- `signal_acknowledged_time`
- `action_initiated_time`
- `action_completed_time`
- `detection_latency_min`
- `acknowledgment_latency_min`
- `action_latency_min`
- `total_latency_min`

---

### 5.3 PostgreSQL Schema

I designed a PostgreSQL-ready schema to support the workflow audit layer.

Core entities include:

- Patients
- Signal sources
- Clinical actors
- Bottlenecks
- Outcomes
- Shifts
- Signal audit events
- Clinician overrides

The schema supports:

- Signal-to-action audit trails
- Patient trajectory analysis
- Bottleneck impact analysis
- Shift performance metrics
- Preventable deterioration flags
- Human-in-the-loop feedback
- Dashboard-ready materialized views

---

### 5.4 Data Quality Layer

The data quality layer checks whether the system should trust the incoming data before scoring or routing it.

Example issues:

- Missing labs
- Impossible vital signs
- Duplicate records
- Backdated vitals
- Clock drift across systems
- Missing acknowledgment time
- Escalation before alert time
- Incomplete documentation
- Inconsistent shift labels

Important rule:

> If a signal is backdated or clock drift is detected, the workflow score can be suppressed and routed to a data review queue.

This prevents unreliable data from triggering false workflow escalation.

---

### 5.5 Workflow Risk Tiering

The system converts risk into action language instead of only displaying raw scores.

| Tier | Meaning | Expected action |
|---|---|---|
| Monitor | No immediate workflow risk | Continue routine observation |
| Review | Signal needs nurse review | Nurse assessment within 30 minutes |
| Escalate | Signal needs clinician action | Resident or order review within 15 minutes |
| Activate | Critical workflow risk | RRT or attending response within 5 minutes |

This makes the output easier to use during real shifts.

Clinicians need clear action language, not unexplained numbers.

---

### 5.6 SLA-Based Escalation Model

The escalation model tracks whether the right person acknowledges and acts within the expected time window.

Example fields:

- `score_tier`
- `escalation_state`
- `sla_target_min`
- `sla_breached`
- `routing_attempts`
- `notification_channel`
- `intervention_type`
- `action_completed_time`

Example routing logic:

| Tier | SLA target | Routing behavior |
|---|---:|---|
| Review | 30 minutes | Route to bedside nurse |
| Escalate | 15 minutes | Route to resident or charge nurse |
| Activate | 5 minutes | Route to RRT or attending |

If acknowledgment latency exceeds the SLA target, the system increments the routing attempt count and routes to the next escalation level.

---

### 5.7 Model-Agnostic Output Structure

Instead of hardcoding every model score into the schema, the system can store model outputs in JSONB.

Example:

```json
{
  "model_type": "rules_v1",
  "raw_risk": 0.78,
  "key_drivers": ["lactate_trend_4h", "hr_variability_drop"],
  "confidence_interval": [0.71, 0.85],
  "fallback_used": false
}
```

This makes the system easier to adapt.

A rules-based engine, gradient boosting model, or future LLM-assisted workflow layer can feed the same routing and dashboard logic.

---

## 6. System Architecture

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

        ↓

Audit and Feedback Loop
Clinician override | Outcome review | Bottleneck analysis | Quality improvement
```

### Architecture principle

The system does not diagnose patients.

It tracks workflow risk.

It asks:

> Which signal needs action, who should act, how fast, and where did the process stall?

---

## 7. Data Design

The dataset was designed around workflow movement, not only clinical values.

| Data area | Example fields |
|---|---|
| Patient context | patient_id, ward, bed, shift |
| Vitals | heart_rate, respiratory_rate, spo2, systolic_bp |
| Labs | lactate, lab_order_time, lab_result_time, lab_delay_minutes |
| Workflow timing | signal_generated_time, detected_time, acknowledged_time, action_initiated_time, action_completed_time |
| Data quality | is_backdated, clock_sync_status, missing_notes, data_quality_flags |
| Escalation | score_tier, escalation_state, sla_target_min, sla_breached, routing_attempts |
| Model output | model_output, confidence, key_drivers |
| Human feedback | override_reason, clinician_action, outcome_correct |

### Why this design matters

Most healthcare data projects focus on patient values.

This project focuses on **how signals move through work**.

That makes it possible to measure where the delay happened:

- Was the signal delayed at detection?
- Was the clinician notification delayed?
- Was acknowledgment delayed?
- Was the order placed but not completed?
- Was documentation incomplete?
- Was the data unreliable?

---

## 8. Dashboard Prototype

The dashboard was designed for scanability, role clarity, and operational action.

### 8.1 Executive Summary Cards

Purpose: Give nurse managers and operations leads a fast view of shift performance.

Example metrics:

| Metric | Example value | Use |
|---|---:|---|
| Average signal-to-action time | 48 minutes | Measures escalation latency |
| Active escalations | 4 | Shows current workload |
| SLA breaches today | 2 | Shows missed escalation targets |
| Alarms suppressed | 1,240 | Shows noise reduction |
| Preventable events flagged | 3 | Supports quality review |

---

### 8.2 High-Risk Patient Queue

Purpose: Replace static rounding lists with a dynamic patient priority view.

Example fields:

| Field | Purpose |
|---|---|
| Bed | Locates the patient |
| Score tier | Shows action level |
| SOFA or EWS context | Gives clinical severity context |
| Four-hour trend | Shows trajectory |
| Primary driver | Explains why the patient is prioritized |
| SLA clock | Shows time remaining |
| Recommended action | Guides next workflow step |

Example copy:

> Activate = RRT or attending within 5 minutes.  
> Escalate = resident order review within 15 minutes.  
> Review = nurse assessment within 30 minutes.  
> Monitor = routine care.

---

### 8.3 Escalation Delay and SLA Tracker

Purpose: Show where signals are stalling in the routing workflow.

Example fields:

| Field | Purpose |
|---|---|
| Patient | Identifies case |
| Escalation state | Shows workflow stage |
| Notification channel | Shows how the alert moved |
| Routing attempts | Shows escalation retries |
| Acknowledgment latency | Shows response delay |
| SLA target | Shows expected time window |
| Status | Shows whether action is needed |

Example callout:

> SLA breach: Resident has not acknowledged sepsis alert for Bed 6. Per routing attempt 3, escalate to attending by phone.

---

### 8.4 Lab Delay and Data Quality Warnings

Purpose: Surface invisible workflow gaps before they distort scoring or delay action.

Example warnings:

| Issue | Workflow impact |
|---|---|
| Blood culture result delayed | Sepsis bundle lag |
| Monitor clock drift detected | Score suppressed |
| Vitals backdated by 35 minutes | Route to data review queue |
| Incomplete handoff note | Visibility gap for incoming shift |

---

### 8.5 Missing Documentation and Visibility Gaps

Purpose: Close the gap between action initiated and action completed.

Example prompts:

| Missing element | Recommended prompt |
|---|---|
| Antibiotic administration | “Antibiotics ordered 18 minutes ago. Has infusion started?” |
| Ventilator check | “Last vent compliance charted 2 hours ago. RT assessment due.” |
| Handoff note | “Handoff incomplete. Two data sources unreviewed by oncoming nurse.” |

---

### 8.6 AI Recommended Workflow Actions

Purpose: Make model output actionable without exposing unnecessary math.

Example recommendation:

**Priority Action: Bed 12**

**Suggested action:** Initiate sepsis workflow review and escalation.

**Rationale:**

- Lactate trending upward over three hours
- New tachycardia
- Delay in acknowledgment
- Documentation gap present
- Data quality acceptable

**Clinician response options:**

- Accept and continue workflow
- Request review
- Override or disagree
- Flag data error

Override reasons may include:

- Chronically abnormal vitals
- Patient already being treated
- Faulty probe or bad lab draw
- Comfort measures only
- Data entry error

---

## 9. UX Copy Principles

The dashboard copy follows three rules.

### 1. Use action language, not raw model language

Instead of:

> Composite risk score: 84.2

Use:

> Tier: Escalate. Resident review needed within 15 minutes.

### 2. Make time visible

Instead of:

> Patient is high risk.

Use:

> Risk escalated 12 minutes ago. SLA breach in 3 minutes.

### 3. Use blameless language

Instead of:

> Nurse missed handoff.

Use:

> Handoff visibility gap: two data sources unreviewed by incoming shift.

This matters because ICU teams already work under pressure. The interface should help them route work, not assign blame.

---

## 10. Before vs After

| Before | After |
|---|---|
| Data scattered across bedside monitors, EMR, labs, pagers, and handoff notes | Unified signal audit trail |
| Static rounding lists | Dynamic high-risk patient queue |
| Alert overload | Prioritized workflow tiers |
| No clear delay visibility | SLA and latency tracking |
| Handoff gaps | Shift-start risk summary |
| Hard to audit escalation | Full signal-to-action history |
| Raw scores without clear action | Monitor, Review, Escalate, Activate |
| Data quality issues hidden | Backdated vitals, clock drift, and missing data flagged before scoring |

---

## 11. Demonstrated Results

This is a synthetic portfolio demo, so the results show system capabilities rather than real clinical outcomes.

### What the demo demonstrates

- Created a synthetic ICU workflow dataset.
- Built an audit trail from signal generation to completed action.
- Added checks for missing data, impossible values, clock drift, and backdated documentation.
- Designed action-driven risk tiers.
- Added SLA tracking and routing logic.
- Created a dashboard prototype for nurse managers, charge nurses, residents, and operations teams.
- Included a human override loop.
- Packaged the workflow into a reusable healthtech product concept.

### Capability summary

| Capability | What it shows |
|---|---|
| Signal audit trail | Tracks how clinical signals move through work |
| Data quality gate | Prevents unreliable data from triggering escalation logic |
| Workflow risk tiering | Converts complex signals into practical action tiers |
| SLA state machine | Makes escalation delays visible |
| Dashboard prototype | Shows the right signal to the right role |
| Human override | Keeps clinicians in control |
| Model-agnostic output | Allows future model changes without redesigning the workflow |

---

## 12. What This Demonstrates

This project demonstrates the ability to connect clinical workflow knowledge, data design, AI-assisted logic, and product UX into one usable system.

### Clinical workflow thinking

I mapped how ICU signals move across people, systems, and time.

### Data systems thinking

I structured synthetic data around events, timestamps, quality issues, and auditability.

### AI product thinking

I separated workflow intelligence from diagnosis to keep the system safer and more operationally useful.

### UX thinking

I translated risk into clear actions, SLA clocks, role-based views, and blameless prompts.

### Implementation thinking

I designed the pipeline, schema, dashboard logic, and human override loop.

---

## 13. Portfolio Positioning

### One-sentence pitch

Clinical Workflow Signal Audit turns fragmented ICU signals into clear escalation paths, faster action, and full auditability.

### For hospital operations managers

This tool gives full visibility into how signals move through the ICU, so leaders can identify delays, enforce standards, and audit every step of escalation.

### For nurse managers

This dashboard organizes scattered patient data into clear priorities, helping teams respond faster, document completely, and hand off care safely.

### For healthtech founders

This is a model-agnostic workflow intelligence layer that can sit between clinical data sources and product interfaces to turn fragmented data into timely, auditable action.

### For Upwork clients

This project shows how messy healthcare workflow data can become a cleaned dataset, validation logic, escalation rules, PostgreSQL schema, and dashboard prototype.

---

## 14. Suggested Portfolio Layout

Use this order on the public portfolio page:

1. Hero section
2. Problem statement
3. Fictional ICU scenario
4. What I built
5. System architecture
6. Dataset design
7. Risk tiering and SLA logic
8. Dashboard prototype
9. Before vs after
10. Demonstrated results
11. What this project demonstrates
12. Call to action

---

## 15. GitHub Repository Structure

```text
clinical-workflow-signal-audit/
│
├── README.md
├── data/
│   ├── raw_icu_workflow_data.csv
│   └── clean_icu_workflow_data.csv
│
├── scripts/
│   └── deepseek_python.py
│
├── sql/
│   └── postgres_schema.sql
│
├── docs/
│   ├── risk_scoring_logic.md
│   ├── dashboard_spec.md
│   └── case_study.md
│
└── assets/
    └── signal_audit_visual_explainer.mp4
```

---

## 16. Implementation Roadmap

### Phase 1: Portfolio demo

- Publish case study page.
- Upload code and schema to GitHub.
- Add visual explainer video.
- Add dashboard screenshots.
- Write LinkedIn launch post.

### Phase 2: Stronger prototype

- Build clickable dashboard in Lovable.
- Add sample CSV download.
- Add dashboard metrics from actual synthetic data.
- Add before-and-after workflow animation.
- Add GitHub README and technical walkthrough.

### Phase 3: Service packaging

Turn the project into a client-facing service:

**Healthcare Workflow Data Cleaning and Escalation Dashboard Prototype**

Potential deliverables:

- Workflow audit map
- Data quality report
- Cleaned dataset
- PostgreSQL schema
- Risk tiering logic
- Dashboard prototype
- Executive summary report

---

## 17. Responsible AI and Data Handling

This demo uses synthetic data only.

It does not use real patient records, protected health information, or hospital-identifiable data.

The system is positioned as workflow intelligence, not diagnostic AI.

It supports clinical teams by improving visibility into signal flow, escalation timing, and operational gaps. It does not replace clinical judgment.

### Safety principles

- Keep clinicians in control.
- Use human override.
- Avoid black-box recommendations.
- Suppress scoring when data quality is poor.
- Show why a signal was routed.
- Audit all workflow decisions.
- Use synthetic or properly governed data for development.

---

## 18. Final Case Study Summary

ICU teams do not only need more alerts. They need better signal flow.

Clinical Workflow Signal Audit shows how fragmented signals from vitals, labs, alarms, documentation, and handoffs can become an auditable workflow intelligence layer.

The demo turns scattered data into:

- A signal audit trail
- Data quality checks
- Action-driven risk tiers
- SLA-based escalation routing
- Role-based dashboard views
- Human override feedback
- Model-agnostic architecture

The result is a portfolio-ready demonstration of how clinical workflow intelligence can make operational risk visible and actionable.

---

## 19. Import Notes for Notion

After importing this file into Notion:

1. Add the visual explainer video near the “Before vs After” section.
2. Add screenshots from the dashboard prototype under “Dashboard Prototype.”
3. Convert the larger tables into Notion databases only if you want filtering.
4. Keep the case study as one page first.
5. Later, split technical details into subpages if the page becomes too long.

