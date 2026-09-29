from app.fhir.workflow_bundle import (
    build_fhir_bundle_from_event,
    build_patient_from_event,
    build_workflow_bundle_from_event,
)


def make_event() -> dict:
    return {
        "event_id": "EVT-00001",
        "patient_id": "PT-98696",
        "signal_type": "Heart Rate",
        "signal_generated_time": "2026-09-27 23:27:17.888957",
        "signal_detected_time": "2026-09-27 23:29:17.888957",
        "workflow_tier": "Review",
        "escalation_state": "Completed",
        "action_initiated_time": "2026-09-27 23:51:17.888957",
        "action_completed_time": "2026-09-27 23:59:17.888957",
    }


def test_patient_is_built_from_event() -> None:
    patient = build_patient_from_event(make_event())

    assert patient.resourceType == "Patient"
    assert patient.id == "PT-98696"


def test_workflow_bundle_preserves_resource_relationships() -> None:
    bundle = build_workflow_bundle_from_event(make_event())

    assert bundle.patient.id == "PT-98696"

    assert bundle.observation.subject is not None
    assert (
        bundle.observation.subject.reference
        == "Patient/PT-98696"
    )

    assert bundle.task.for_ is not None
    assert (
        bundle.task.for_.reference
        == "Patient/PT-98696"
    )

    assert bundle.task.focus is not None
    assert (
        bundle.task.focus.reference
        == "Observation/EVT-00001-observation"
    )


def test_fhir_bundle_contains_related_resources() -> None:
    bundle = build_fhir_bundle_from_event(make_event())

    assert bundle.resourceType == "Bundle"
    assert bundle.type == "collection"
    assert len(bundle.entry) == 3

    resources = [
        entry.resource
        for entry in bundle.entry
    ]

    assert [resource.resourceType for resource in resources] == [
        "Patient",
        "Observation",
        "Task",
    ]


def test_fhir_bundle_preserves_cross_resource_references() -> None:
    bundle = build_fhir_bundle_from_event(make_event())

    patient = bundle.entry[0].resource
    observation = bundle.entry[1].resource
    task = bundle.entry[2].resource

    patient_url = (
        "https://github.com/arapkirui513-hub/"
        "clinical-workflow-signal-audit/Patient/PT-98696"
    )

    observation_url = (
        "https://github.com/arapkirui513-hub/"
        "clinical-workflow-signal-audit/"
        "Observation/EVT-00001-observation"
    )

    assert patient.id == "PT-98696"

    assert observation.subject is not None
    assert observation.subject.reference == patient_url

    assert task.for_ is not None
    assert task.for_.reference == patient_url

    assert task.focus is not None
    assert task.focus.reference == observation_url


def test_fhir_bundle_entries_have_consistent_full_urls() -> None:
    bundle = build_fhir_bundle_from_event(make_event())

    patient_url = (
        "https://github.com/arapkirui513-hub/"
        "clinical-workflow-signal-audit/Patient/PT-98696"
    )

    observation_url = (
        "https://github.com/arapkirui513-hub/"
        "clinical-workflow-signal-audit/"
        "Observation/EVT-00001-observation"
    )

    task_url = (
        "https://github.com/arapkirui513-hub/"
        "clinical-workflow-signal-audit/Task/"
        "e0e0c77b-0664-5e4e-84e1-5bf459b37b93"
    )

    assert bundle.entry[0].fullUrl == patient_url
    assert bundle.entry[1].fullUrl == observation_url
    assert bundle.entry[2].fullUrl == task_url

    observation = bundle.entry[1].resource
    task = bundle.entry[2].resource

    assert observation.subject is not None
    assert observation.subject.reference == patient_url

    assert task.for_ is not None
    assert task.for_.reference == patient_url

    assert task.focus is not None
    assert task.focus.reference == observation_url