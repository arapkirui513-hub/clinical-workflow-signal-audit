from app.fhir.synthetic_events import (
    DATASET_PATH,
    build_observations_from_dataset,
    load_synthetic_events,
)


def test_synthetic_dataset_exists() -> None:
    assert DATASET_PATH.exists()


def test_synthetic_dataset_contains_500_events() -> None:
    events = load_synthetic_events()

    assert len(events) == 500


def test_synthetic_events_have_required_fields() -> None:
    events = load_synthetic_events()

    required_fields = {
        "event_id",
        "patient_id",
        "signal_type",
        "signal_generated_time",
    }

    for event in events:
        assert required_fields.issubset(event.keys())


def test_observation_count_matches_event_count() -> None:
    events = load_synthetic_events()
    observations = build_observations_from_dataset()

    assert len(observations) == len(events)


def test_observation_ids_are_deterministic() -> None:
    observations = build_observations_from_dataset()

    ids = [observation.id for observation in observations]

    assert ids[0] == "EVT-00001-observation"
    assert len(ids) == len(set(ids))


def test_observations_reference_source_patients() -> None:
    observations = build_observations_from_dataset()

    for observation in observations:
        assert observation.subject is not None
        assert observation.subject.reference.startswith(
            "Patient/"
        )


def test_observations_have_no_measurement_values() -> None:
    observations = build_observations_from_dataset()

    for observation in observations:
        payload = observation.model_dump(
            exclude_none=True
        )

        assert "value" not in payload
        assert "valueQuantity" not in payload
        assert "valueCodeableConcept" not in payload
        assert "valueString" not in payload


def test_observations_have_data_absent_reason() -> None:
    observations = build_observations_from_dataset()

    for observation in observations:
        assert observation.dataAbsentReason is not None

        coding = observation.dataAbsentReason.coding[0]

        assert coding.code == "unsupported"