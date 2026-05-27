# Dashboard Specification

## Dashboard name

Signal Audit ICU Dashboard

## Purpose

The dashboard gives nurse managers, charge nurses, residents, and operations teams a real-time view of workflow risk, escalation status, and data quality.

## Main sections

### 1. Operations Overview

Metrics:

- Average signal-to-action time
- Active escalations
- SLA breaches today
- Alarms suppressed
- Preventable events flagged

### 2. High-Risk Patient Queue

Columns:

- Bed
- Patient
- Score tier
- SOFA
- Four-hour trend
- Primary driver
- SLA clock
- Recommended action

### 3. AI Recommended Action

Shows:

- Subject
- Recommendation
- Rationale
- Confidence
- Accept, review, and override controls

### 4. Escalation SLA Tracker

Shows:

- Escalation ID
- Bed
- Notification channel
- Routing attempts
- Acknowledgment latency
- SLA target
- Status

### 5. Lab Delay and Data Quality

Shows:

- Delayed labs
- Backdated vitals
- Clock drift
- Score suppression
- Pipeline health

## UX principles

- Use action language, not raw model language.
- Make time visible.
- Use blameless language.
- Keep clinicians in control.
- Suppress scoring when data quality is unreliable.
