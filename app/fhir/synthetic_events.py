from pathlib import Path

import pandas as pd

from app.fhir.observation import (
    FHIRObservation,
    build_observation_from_event,
)


DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "generated"
    / "synthetic_icu_workflow.csv"
)


def load_synthetic_events() -> list[dict]:
    """
    Load the reproducible synthetic ICU workflow dataset.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Synthetic dataset not found: {DATASET_PATH}"
        )

    dataframe = pd.read_csv(DATASET_PATH)

    return dataframe.to_dict(orient="records")


def build_observations_from_dataset() -> list[FHIRObservation]:
    """
    Convert every synthetic workflow event into
    a FHIR Observation.
    """

    events = load_synthetic_events()

    return [
        build_observation_from_event(event)
        for event in events
    ]