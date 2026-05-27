# Risk Tiering and Escalation Logic

## Purpose

The system translates fragmented ICU workflow signals into action-driven tiers.

The goal is not diagnosis. The goal is workflow routing.

## Tiers

| Tier | Workflow meaning | SLA target | Recommended route |
|---|---|---:|---|
| Monitor | Routine observation | No escalation SLA | Continue monitoring |
| Review | Nurse review needed | 30 minutes | Bedside nurse |
| Escalate | Clinician review needed | 15 minutes | Resident or charge nurse |
| Activate | Critical workflow risk | 5 minutes | RRT or attending |

## Example routing rule

```text
IF score_tier = Activate
AND acknowledgment_latency_min > 5
THEN sla_breached = TRUE
AND routing_attempts += 1
AND route_to = next_escalation_level
```

## Data quality gate

Scores should be suppressed when data quality is unreliable.

Examples:

```text
IF is_backdated = TRUE
OR clock_sync_status = drift_detected
OR missing_inputs > 2
THEN composite_risk_score = NULL
AND route_to = data_review_queue
```

## Model-agnostic output

Store model outputs in JSONB so the routing layer can work with different model types.

```json
{
  "model_type": "rules_v1",
  "raw_risk": 0.78,
  "key_drivers": ["lactate_trend_4h", "hr_variability_drop"],
  "confidence_interval": [0.71, 0.85],
  "fallback_used": false
}
```

## Interface rule

Clinicians should see workflow action language first.

Use:

```text
Tier: Escalate
Resident review needed within 15 minutes
```

Avoid leading with:

```text
Composite risk score: 84.2
```
