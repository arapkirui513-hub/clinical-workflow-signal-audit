"""
Clinical Workflow Signal Audit
Evidence Metrics Generator

Reads the generated synthetic workflow dataset and produces
reproducible evidence for documentation and portfolio case studies.

Author: Kevin Kirui
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


# ==========================================================
# Configuration
# ==========================================================

DATASET_PATH = Path(
    "data/generated/synthetic_icu_workflow.csv"
)

OUTPUT_DIR = Path("output")

MARKDOWN_REPORT = OUTPUT_DIR / "evidence_report.md"

JSON_REPORT = OUTPUT_DIR / "metrics.json"


# ==========================================================
# Dataset Loading
# ==========================================================

def load_dataset() -> pd.DataFrame:
    """
    Load the generated workflow dataset.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    return pd.read_csv(
        DATASET_PATH,
        parse_dates=[
            "signal_generated_time",
            "signal_detected_time",
            "signal_acknowledged_time",
            "action_initiated_time",
            "action_completed_time",
        ],
    )


# ==========================================================
# Dataset Validation
# ==========================================================

def validate_dataset(df: pd.DataFrame):
    """
    Ensure required columns exist before
    calculating metrics.
    """

    required_columns = [
        "event_id",
        "patient_id",
        "hospital_unit",
        "signal_type",
        "workflow_tier",
        "escalation_state",
        "sla_breached",
        "routing_attempts",
        "data_quality_issue",
        "total_latency_min",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    return True


# ==========================================================
# Utility Functions
# ==========================================================

def percentage(
    numerator,
    denominator,
):
    """
    Calculate percentage safely.
    """

    if denominator == 0:
        return 0.0

    return round(
        100 * numerator / denominator,
        1,
    )


# ==========================================================
# Metric Calculations
# ==========================================================

def calculate_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate all reproducible workflow evidence metrics.
    """

    workflow_events = len(df)

    unique_patients = df["patient_id"].nunique()

    workflow_tiers = (
        df["workflow_tier"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    hospital_units = (
        df["hospital_unit"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    signal_types = (
        df["signal_type"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    escalation_states = (
        df["escalation_state"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    routing = {
        "mean": round(df["routing_attempts"].mean(), 2),
        "maximum": int(df["routing_attempts"].max()),
    }

    latency = {
        "mean": round(df["total_latency_min"].mean(), 1),
        "median": round(df["total_latency_min"].median(), 1),
        "minimum": int(df["total_latency_min"].min()),
        "maximum": int(df["total_latency_min"].max()),
        "std_dev": round(df["total_latency_min"].std(), 2),
    }

    sla_breaches = int(df["sla_breached"].sum())

    sla = {
        "breaches": sla_breaches,
        "compliance_percent": percentage(
            workflow_events - sla_breaches,
            workflow_events,
        ),
    }

    data_quality_breakdown = (
        df["data_quality_issue"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    records_with_issues = (
        workflow_events
        - data_quality_breakdown.get("None", 0)
    )

    data_quality = {
        "records_with_issues": records_with_issues,
        "percentage": percentage(
            records_with_issues,
            workflow_events,
        ),
        "breakdown": data_quality_breakdown,
    }

    sla_by_workflow_tier = {}

    latency_by_workflow_tier = {}

    for tier in sorted(df["workflow_tier"].unique()):

        tier_df = df[df["workflow_tier"] == tier]

        breaches = int(
            tier_df["sla_breached"].sum()
        )

        sla_by_workflow_tier[tier] = {
            "events": len(tier_df),
            "breaches": breaches,
            "compliance_percent": percentage(
                len(tier_df) - breaches,
                len(tier_df),
            ),
        }

        latency_by_workflow_tier[tier] = {
            "events": len(tier_df),
            "mean": round(
                tier_df["total_latency_min"].mean(),
                1,
            ),
            "median": round(
                tier_df["total_latency_min"].median(),
                1,
            ),
            "minimum": int(
                tier_df["total_latency_min"].min()
            ),
            "maximum": int(
                tier_df["total_latency_min"].max()
            ),
        }

    return {

        "workflow_volume": {
            "workflow_events": workflow_events,
            "unique_patients": unique_patients,
        },

        "workflow_tiers": workflow_tiers,

        "hospital_units": hospital_units,

        "signal_types": signal_types,

        "escalation_states": escalation_states,

        "routing": routing,

        "latency": latency,

        "latency_by_workflow_tier": latency_by_workflow_tier,

        "sla": sla,

        "sla_by_workflow_tier": sla_by_workflow_tier,

        "data_quality": data_quality,
    }


# ==========================================================
# Export Functions
# ==========================================================

def export_json(metrics: dict) -> None:
    """
    Export metrics as machine-readable JSON.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        JSON_REPORT,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )


def export_markdown(metrics: dict) -> None:
    """
    Export a human-readable evidence report.
    """

    report = [
        "# Clinical Workflow Signal Audit",
        "",
        "## Evidence Report",
        "",
        f"Generated from `{DATASET_PATH}`",
        "",
        "## Workflow Volume",
        f"- Workflow events: {metrics['workflow_volume']['workflow_events']}",
        f"- Unique patients: {metrics['workflow_volume']['unique_patients']}",
        "",
        "## SLA Performance",
        f"- Compliance: {metrics['sla']['compliance_percent']}%",
        f"- Breaches: {metrics['sla']['breaches']}",
        "",
        "## Latency",
        f"- Mean: {metrics['latency']['mean']} min",
        f"- Median: {metrics['latency']['median']} min",
        f"- Minimum: {metrics['latency']['minimum']} min",
        f"- Maximum: {metrics['latency']['maximum']} min",
        "",
        "## Latency by Workflow Tier",
    ]

    for tier, values in metrics["latency_by_workflow_tier"].items():
        report.extend(
            [
                "",
                f"### {tier}",
                f"- Events: {values['events']}",
                f"- Mean latency: {values['mean']} min",
                f"- Median latency: {values['median']} min",
                f"- Range: {values['minimum']}–{values['maximum']} min",
            ]
        )

    report.extend(
        [
            "",
            "## Data Quality",
            f"- Records with issues: {metrics['data_quality']['records_with_issues']}",
            f"- Percentage affected: {metrics['data_quality']['percentage']}%",
            "",
            "## Generated Files",
            f"- JSON: `{JSON_REPORT}`",
            f"- Markdown: `{MARKDOWN_REPORT}`",
        ]
    )

    with open(
        MARKDOWN_REPORT,
        "w",
        encoding="utf-8",
    ) as file:
        file.write("\n".join(report))


# ==========================================================
# Terminal Summary
# ==========================================================

def print_summary(metrics: dict) -> None:
    """
    Print a concise summary after evidence generation.
    """

    print()
    print("=" * 60)
    print("Evidence Generation Complete")
    print("=" * 60)

    print(
        f"Workflow Events      : {metrics['workflow_volume']['workflow_events']}"
    )

    print(
        f"Unique Patients      : {metrics['workflow_volume']['unique_patients']}"
    )

    print(
        f"SLA Compliance       : {metrics['sla']['compliance_percent']}%"
    )

    print(
        f"SLA Breaches         : {metrics['sla']['breaches']}"
    )

    print(
        f"Median Latency       : {metrics['latency']['median']} min"
    )

    print(
        f"Records with Issues  : {metrics['data_quality']['records_with_issues']}"
    )

    print()
    print(f"JSON Report      : {JSON_REPORT}")
    print(f"Markdown Report  : {MARKDOWN_REPORT}")

    print("=" * 60)


# ==========================================================
# Main
# ==========================================================

def main() -> None:

    df = load_dataset()

    validate_dataset(df)

    metrics = calculate_metrics(df)

    export_json(metrics)

    export_markdown(metrics)

    print_summary(metrics)


if __name__ == "__main__":
    main()