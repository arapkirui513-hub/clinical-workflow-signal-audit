"""
Clinical Workflow Signal Audit
Synthetic Dataset Generator

Generates a reproducible synthetic workflow dataset based on
Simulation Specification v1.0.

Author: Kevin Kirui
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# ==========================================================
# Configuration
# ==========================================================

RANDOM_SEED = 42
NUMBER_OF_EVENTS = 500

OUTPUT_DIR = Path("data/generated")
OUTPUT_FILE = OUTPUT_DIR / "synthetic_icu_workflow.csv"

random.seed(RANDOM_SEED)


# ==========================================================
# Simulation Constants
# ==========================================================

HOSPITAL_UNITS = [
    "ICU",
    "HDU",
    "Emergency Department",
    "Medical Ward",
    "Surgical Ward",
]

UNIT_WEIGHTS = [
    0.60,
    0.15,
    0.10,
    0.10,
    0.05,
]

SIGNAL_TYPES = [
    "Heart Rate",
    "Blood Pressure",
    "Respiratory Rate",
    "Oxygen Saturation",
    "Temperature",
    "Lactate",
]

SIGNAL_WEIGHTS = [
    0.22,
    0.20,
    0.18,
    0.18,
    0.12,
    0.10,
]

WORKFLOW_TIERS = {
    "Monitor": 0.45,
    "Review": 0.30,
    "Escalate": 0.18,
    "Activate": 0.07,
}

SLA_TARGETS = {
    "Monitor": None,
    "Review": 30,
    "Escalate": 15,
    "Activate": 5,
}

ESCALATION_STATES = [
    "Pending",
    "Acknowledged",
    "Completed",
]

ESCALATION_WEIGHTS = [
    0.08,
    0.22,
    0.70,
]

DATA_QUALITY_ISSUES = [
    "None",
    "Missing Lab",
    "Clock Drift",
    "Backdated Vital",
    "Duplicate Record",
    "Missing Documentation",
]

DATA_QUALITY_WEIGHTS = [
    0.88,
    0.03,
    0.02,
    0.02,
    0.03,
    0.02,
]


# ==========================================================
# Helper Functions
# ==========================================================

def weighted_choice(options, weights):
    """Return one weighted random choice."""
    return random.choices(options, weights=weights, k=1)[0]


def generate_patient_id() -> str:
    """Generate a synthetic patient identifier."""
    return f"PT-{random.randint(10000, 99999)}"


def generate_event_id(index: int) -> str:
    """Generate a workflow event identifier."""
    return f"EVT-{index:05d}"


def generate_base_timestamp() -> datetime:
    """
    Generate a timestamp within the previous 30 days.
    """
    now = datetime.now()

    return now - timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def assign_workflow_tier() -> str:
    """Assign workflow tier using specification weights."""
    return weighted_choice(
        list(WORKFLOW_TIERS.keys()),
        list(WORKFLOW_TIERS.values()),
    )


def assign_signal_type() -> str:
    """Assign signal type."""
    return weighted_choice(
        SIGNAL_TYPES,
        SIGNAL_WEIGHTS,
    )


def assign_hospital_unit() -> str:
    """Assign originating hospital unit."""
    return weighted_choice(
        HOSPITAL_UNITS,
        UNIT_WEIGHTS,
    )


def assign_escalation_state() -> str:
    """Assign workflow completion state."""
    return weighted_choice(
        ESCALATION_STATES,
        ESCALATION_WEIGHTS,
    )


def assign_data_quality_issue() -> str:
    """Assign data quality issue."""
    return weighted_choice(
        DATA_QUALITY_ISSUES,
        DATA_QUALITY_WEIGHTS,
    )


# ==========================================================
# Workflow Timeline Generation
# ==========================================================

def generate_workflow_timestamps(
    signal_generated_time: datetime,
    workflow_tier: str,
):
    """
    Generate realistic workflow timestamps based on workflow tier.

    Returns:
        (
            detected_time,
            acknowledged_time,
            action_started_time,
            action_completed_time,
            detection_latency,
            acknowledgement_latency,
            action_latency,
            total_latency,
        )
    """

    if workflow_tier == "Monitor":
        detection_latency = random.randint(3, 8)
        acknowledgement_latency = random.randint(10, 25)
        action_latency = random.randint(15, 35)

    elif workflow_tier == "Review":
        detection_latency = random.randint(2, 6)
        acknowledgement_latency = random.randint(5, 15)
        action_latency = random.randint(10, 25)

    elif workflow_tier == "Escalate":
        detection_latency = random.randint(1, 4)
        acknowledgement_latency = random.randint(3, 8)
        action_latency = random.randint(5, 15)

    else:  # Activate
        detection_latency = random.randint(0, 2)
        acknowledgement_latency = random.randint(1, 5)
        action_latency = random.randint(2, 10)

    detected_time = signal_generated_time + timedelta(
        minutes=detection_latency
    )

    acknowledged_time = detected_time + timedelta(
        minutes=acknowledgement_latency
    )

    action_started_time = acknowledged_time + timedelta(
        minutes=action_latency
    )

    action_completed_time = action_started_time + timedelta(
        minutes=random.randint(5, 20)
    )

    total_latency = (
        detection_latency
        + acknowledgement_latency
        + action_latency
    )

    return (
        detected_time,
        acknowledged_time,
        action_started_time,
        action_completed_time,
        detection_latency,
        acknowledgement_latency,
        action_latency,
        total_latency,
    )


# ==========================================================
# Workflow Logic
# ==========================================================

def calculate_sla_breach(
    workflow_tier: str,
    total_latency: int,
) -> bool:
    """
    Determine whether workflow exceeded its SLA target.
    """

    sla_target = SLA_TARGETS[workflow_tier]

    if sla_target is None:
        return False

    return total_latency > sla_target


def generate_routing_attempts(
    workflow_tier: str,
) -> int:
    """
    Higher-acuity workflows are more likely
    to require additional routing attempts.
    """

    if workflow_tier == "Monitor":
        return random.choices(
            [1, 2],
            weights=[0.95, 0.05],
        )[0]

    if workflow_tier == "Review":
        return random.choices(
            [1, 2],
            weights=[0.85, 0.15],
        )[0]

    if workflow_tier == "Escalate":
        return random.choices(
            [1, 2, 3],
            weights=[0.70, 0.20, 0.10],
        )[0]

    return random.choices(
        [1, 2, 3],
        weights=[0.55, 0.30, 0.15],
    )[0]


# ==========================================================
# Event Generator
# ==========================================================

def generate_event(index: int):
    """
    Generate one complete workflow event.
    """

    workflow_tier = assign_workflow_tier()

    signal_generated_time = generate_base_timestamp()

    (
        detected_time,
        acknowledged_time,
        action_started_time,
        action_completed_time,
        detection_latency,
        acknowledgement_latency,
        action_latency,
        total_latency,
    ) = generate_workflow_timestamps(
        signal_generated_time,
        workflow_tier,
    )

    return {
        "event_id": generate_event_id(index),
        "patient_id": generate_patient_id(),
        "hospital_unit": assign_hospital_unit(),
        "signal_type": assign_signal_type(),

        "signal_generated_time": signal_generated_time,

        "signal_detected_time": detected_time,

        "signal_acknowledged_time": acknowledged_time,

        "action_initiated_time": action_started_time,

        "action_completed_time": action_completed_time,

        "detection_latency_min": detection_latency,

        "acknowledgement_latency_min": acknowledgement_latency,

        "action_latency_min": action_latency,

        "total_latency_min": total_latency,

        "workflow_tier": workflow_tier,

        "escalation_state": assign_escalation_state(),

        "sla_target_min": SLA_TARGETS[workflow_tier],

        "sla_breached": calculate_sla_breach(
            workflow_tier,
            total_latency,
        ),

        "routing_attempts": generate_routing_attempts(
            workflow_tier,
        ),

        "data_quality_issue": assign_data_quality_issue(),
    }


# ==========================================================
# Dataset Generation
# ==========================================================

def generate_dataset(
    number_of_events: int = NUMBER_OF_EVENTS,
) -> pd.DataFrame:
    """
    Generate the complete synthetic workflow dataset.
    """

    events = [
        generate_event(index + 1)
        for index in range(number_of_events)
    ]

    df = pd.DataFrame(events)

    return df


# ==========================================================
# Dataset Validation
# ==========================================================

def validate_dataset(df: pd.DataFrame):
    """
    Perform lightweight validation checks to ensure
    the generated dataset satisfies the simulation
    specification.
    """

    required_columns = [
        "event_id",
        "patient_id",
        "hospital_unit",
        "signal_type",
        "signal_generated_time",
        "signal_detected_time",
        "signal_acknowledged_time",
        "action_initiated_time",
        "action_completed_time",
        "detection_latency_min",
        "acknowledgement_latency_min",
        "action_latency_min",
        "total_latency_min",
        "workflow_tier",
        "escalation_state",
        "sla_target_min",
        "sla_breached",
        "routing_attempts",
        "data_quality_issue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if len(df) != NUMBER_OF_EVENTS:
        raise ValueError(
            f"Expected {NUMBER_OF_EVENTS} events, "
            f"found {len(df)}."
        )

    if df["event_id"].duplicated().any():
        raise ValueError(
            "Duplicate event IDs detected."
        )

    if df["patient_id"].isnull().any():
        raise ValueError(
            "Patient IDs contain null values."
        )

    return True


# ==========================================================
# CSV Export
# ==========================================================

def save_dataset(
    df: pd.DataFrame,
):
    """
    Save the generated dataset as CSV.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()

    print("=" * 55)
    print("Synthetic Workflow Dataset Generated")
    print("=" * 55)

    print(f"Rows           : {len(df)}")
    print(f"Columns        : {len(df.columns)}")
    print(f"Output         : {OUTPUT_FILE}")

    print("=" * 55)


    # ==========================================================
# Simulation Summary
# ==========================================================

def print_simulation_summary(
    df: pd.DataFrame,
):
    """
    Print a concise summary of the generated simulation.
    """

    print()
    print("=" * 60)
    print("Simulation Summary")
    print("=" * 60)

    print(f"Workflow Events      : {len(df)}")
    print(f"Unique Patients      : {df['patient_id'].nunique()}")

    print()

    print("Workflow Tier Distribution")

    tier_counts = (
        df["workflow_tier"]
        .value_counts()
        .reindex(
            [
                "Monitor",
                "Review",
                "Escalate",
                "Activate",
            ],
            fill_value=0,
        )
    )

    for tier, count in tier_counts.items():
        print(f"  {tier:<10} : {count}")

    print()

    sla_breaches = df["sla_breached"].sum()

    print(f"SLA Breaches         : {sla_breaches}")

    compliance = (
        100
        * (len(df) - sla_breaches)
        / len(df)
    )

    print(f"SLA Compliance       : {compliance:.1f}%")

    print()

    dq_issues = (
        df["data_quality_issue"] != "None"
    ).sum()

    print(f"Data Quality Issues  : {dq_issues}")

    print()

    print("Latency (minutes)")

    print(
        f"  Mean              : "
        f"{df['total_latency_min'].mean():.1f}"
    )

    print(
        f"  Median            : "
        f"{df['total_latency_min'].median():.1f}"
    )

    print(
        f"  Minimum           : "
        f"{df['total_latency_min'].min()}"
    )

    print(
        f"  Maximum           : "
        f"{df['total_latency_min'].max()}"
    )

    print()

    print(f"Dataset saved to:")

    print(f"  {OUTPUT_FILE}")

    print("=" * 60)


# ==========================================================
# Main
# ==========================================================

def main():
    """
    Generate, validate, save,
    and summarize the simulation.
    """

    df = generate_dataset()

    validate_dataset(df)

    save_dataset(df)

    print_simulation_summary(df)


if __name__ == "__main__":
    main()