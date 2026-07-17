# Simulation Specification

**Version:** 1.0

**Status:** Active

**Owner:** Kevin Kirui

**Last Updated:** July 2026

---

# 1. Purpose

The Simulation Specification defines the standard for generating synthetic healthcare workflow datasets used throughout this portfolio.

Its purpose is to ensure that every simulation is reproducible, transparent, internally consistent, and suitable for demonstrating workflow intelligence concepts without relying on real patient information.

The specification separates simulation design from implementation. Simulation behavior is defined by this document, while generation scripts implement the specification.

All synthetic workflow datasets must follow this specification.

Simulation scripts adapt to the specification. The specification does not adapt to individual projects.

---

# 2. Design Principles

## Principle 1 – Reproducibility

Every simulation must be reproducible using a fixed random seed.

Running the same generator script with the same specification should produce identical outputs.

---

## Principle 2 – Transparency

Every generated value must have a documented purpose.

Assumptions, probability distributions, and workflow rules must be explicitly defined.

No undocumented randomness is permitted.

---

## Principle 3 – Workflow First

Datasets model healthcare workflows rather than diseases.

Each record represents a workflow event occurring within an operational process.

Clinical values exist only to support workflow behavior.

---

## Principle 4 – Operational Realism

Generated data should reflect realistic healthcare operations without attempting to reproduce any individual patient or hospital.

Workflow timings, escalation behavior, routing, and data quality issues should remain plausible within normal clinical operations.

---

## Principle 5 – Evidence Generation

Synthetic datasets exist to generate measurable evidence.

Every simulation should produce reproducible operational metrics suitable for documentation within portfolio case studies.

---

## Principle 6 – Extensibility

The specification should support future healthcare workflow simulations including ICU, Emergency Department, Radiology, Laboratory, Outpatient, and other operational environments without requiring structural redesign.

---

# 3. Dataset Specification

## Dataset Size

Default simulation size:

- 500 workflow events

Dataset size may be increased or decreased for specific demonstrations while maintaining reproducibility.

---

## Record Definition

Each row represents one workflow event.

A workflow event follows a signal from generation through operational completion.

---

## Required Fields

Every generated dataset must contain the following fields.

### Identification

- event_id
- patient_id
- ward

### Clinical Signal

- signal_type
- signal_generated_time

### Workflow Timeline

- signal_detected_time
- signal_acknowledged_time
- action_initiated_time
- action_completed_time

### Derived Metrics

- detection_latency_min
- acknowledgment_latency_min
- action_latency_min
- total_latency_min

### Workflow Classification

- workflow_tier
- escalation_state
- sla_target_min
- sla_breached
- routing_attempts

### Data Quality

- data_quality_issue

---

# 4. Simulation Rules

## Workflow Tiers

The default workflow distribution is:

| Tier | Target Distribution |
|-------|--------------------:|
| Monitor | 45% |
| Review | 30% |
| Escalate | 18% |
| Activate | 7% |

These values represent operational workload rather than disease prevalence.

---

## Signal Types

Default signal categories include:

- Heart Rate
- Blood Pressure
- Respiratory Rate
- Oxygen Saturation
- Lactate
- Temperature

Future simulations may extend this list.

---

## SLA Targets

| Tier | Target |
|------|--------:|
| Monitor | No SLA |
| Review | 30 minutes |
| Escalate | 15 minutes |
| Activate | 5 minutes |

---

## Routing Attempts

Routing attempts should range from one to three.

Most events should require a single routing attempt.

Repeated routing attempts should become progressively less common.

---

## Data Quality Issues

Approximately 10–15% of workflow events should contain one documented data quality issue.

Permitted values include:

- None
- Missing Lab
- Clock Drift
- Backdated Vital
- Duplicate Record
- Missing Documentation

---

# 5. Evidence Generation

Every simulation must support automatic generation of operational evidence.

At minimum, the following metrics should be produced.

## Workflow Volume

- Total workflow events
- Unique patients
- Workflow tier distribution

## Latency

- Mean latency
- Median latency
- Minimum latency
- Maximum latency

## SLA Performance

- SLA compliance rate
- SLA breach count

## Workflow Performance

- Average routing attempts
- Escalation state distribution

## Data Quality

- Data quality issue count
- Percentage of affected records

These metrics form the evidence base for project documentation.

---

# 6. Implementation Requirements

Simulation scripts must:

- use a fixed random seed;
- generate reproducible datasets;
- calculate derived workflow metrics automatically;
- export datasets as CSV;
- support automated evidence generation.

Implementation details belong to code rather than this specification.

---

# 7. Evolution Policy

This specification evolves only when multiple healthcare workflow simulations reveal the same structural limitation.

Project-specific requirements should be addressed within individual simulation scripts rather than modifying the specification.

---

# Revision History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | July 2026 | Initial simulation specification for synthetic healthcare workflow datasets. |