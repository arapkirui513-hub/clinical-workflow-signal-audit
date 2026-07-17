# Clinical Workflow Signal Audit

## Evidence Report

Generated from `data\generated\synthetic_icu_workflow.csv`

## Workflow Volume
- Workflow events: 500
- Unique patients: 497

## SLA Performance
- Compliance: 63.8%
- Breaches: 181

## Latency
- Mean: 34.4 min
- Median: 36.0 min
- Minimum: 3 min
- Maximum: 67 min

## Latency by Workflow Tier

### Activate
- Events: 36
- Mean latency: 10.1 min
- Median latency: 10.0 min
- Range: 3–16 min

### Escalate
- Events: 89
- Mean latency: 17.2 min
- Median latency: 17.0 min
- Range: 10–27 min

### Monitor
- Events: 218
- Mean latency: 47.2 min
- Median latency: 47.0 min
- Range: 32–67 min

### Review
- Events: 157
- Mean latency: 32.1 min
- Median latency: 32.0 min
- Range: 20–45 min

## Data Quality
- Records with issues: 500
- Percentage affected: 100.0%

## Generated Files
- JSON: `output\metrics.json`
- Markdown: `output\evidence_report.md`