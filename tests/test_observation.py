from fastapi.testclient import TestClient

from app.fhir.observation import (
    build_observation_code,
    build_observation_from_event,
)
from app.main import app


client = TestClient(app)


def make_event(
    signal_type: str = "Heart Rate",
) -> dict:
    return {
        "event_id": "EVT-0001",
        "patient_id": "PAT-0001",
        "signal_type": signal_type,
        "signal_generated_time": "2026-07-16T19:23:38",
    }


def test_heart_rate_uses_loinc_and_local_code() -> None:
    observation = build_observation_code("Heart Rate")

    codes = observation.coding

    assert any(
        coding.system == "http://loinc.org"
        and coding.code == "8867-4"
        for coding in codes
    )

    assert any(
        coding.system.endswith("/CodeSystem/signal-type")
        and coding.code == "heart-rate"
        for coding in codes
    )


def test_observation_has_no_measurement_value() -> None:
    observation = build_observation_from_event(
        make_event()
    )

    payload = observation.model_dump(
        exclude_none=True
    )

    assert "valueQuantity" not in payload
    assert "valueCodeableConcept" not in payload
    assert "valueString" not in payload
    assert "value" not in payload


def test_observation_marks_missing_value_as_unsupported() -> None:
    observation = build_observation_from_event(
        make_event()
    )

    assert observation.dataAbsentReason is not None

    coding = observation.dataAbsentReason.coding[0]

    assert (
        coding.system
        == "http://terminology.hl7.org/CodeSystem/data-absent-reason"
    )

    assert coding.code == "unsupported"


def test_observation_references_patient() -> None:
    observation = build_observation_from_event(
        make_event()
    )

    assert observation.subject is not None
    assert observation.subject.reference == "Patient/PAT-0001"


def test_observation_uses_signal_generated_time() -> None:
    observation = build_observation_from_event(
        make_event()
    )

    assert (
        observation.effectiveDateTime
        == "2026-07-16T19:23:38.000000Z"
    )


def test_unmapped_signal_keeps_local_code_only() -> None:
    observation = build_observation_code(
        "Blood Pressure"
    )

    assert len(observation.coding) == 1

    coding = observation.coding[0]

    assert (
    coding.system
    == "https://github.com/arapkirui513-hub/clinical-workflow-signal-audit/CodeSystem/signal-type"
    )

    assert coding.code == "blood-pressure"


def test_create_and_get_observation() -> None:
    observation = {
        "resourceType": "Observation",
        "id": "EVT-0001-observation",
        "status": "unknown",
        "category": [
            {
                "coding": [
                    {
                        "system": (
                            "https://github.com/arapkirui513-hub/"
                            "clinical-workflow-signal-audit/CodeSystem/record-kind"
                        ),
                        "code": "workflow-signal",
                        "display": "Workflow signal",
                    }
                ],
                "text": "Workflow signal",
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8867-4",
                    "display": "Heart rate",
                },
                {
                    "system": (
                        "https://github.com/arapkirui513-hub/"
                        "clinical-workflow-signal-audit/CodeSystem/signal-type"
                    ),
                    "code": "heart-rate",
                    "display": "Heart Rate",
                },
            ],
            "text": "Heart Rate",
        },
        "subject": {
            "reference": "Patient/PAT-0001",
        },
        "effectiveDateTime": "2026-07-16T19:23:38.000000Z",
        "dataAbsentReason": {
            "coding": [
                {
                    "system": (
                        "http://terminology.hl7.org/"
                        "CodeSystem/data-absent-reason"
                    ),
                    "code": "unsupported",
                    "display": "Unsupported",
                }
            ],
            "text": (
                "Measurement value is not represented "
                "in the source dataset."
            ),
        },
        "note": [
            {
                "text": (
                    "Synthetic workflow event. "
                    "Source dataset contains no "
                    "measurement values."
                )
            }
        ],
    }

    response = client.post(
        "/fhir/Observation",
        json=observation,
    )

    assert response.status_code == 201
    assert response.json() == observation

    response = client.get(
        "/fhir/Observation/EVT-0001-observation"
    )

    assert response.status_code == 200
    assert response.json() == observation


def test_observation_not_found() -> None:
    response = client.get(
        "/fhir/Observation/does-not-exist"
    )

    assert response.status_code == 404