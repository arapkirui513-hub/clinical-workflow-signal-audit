from fastapi.testclient import TestClient
import pytest

from app.fhir.task import (
    FHIRTask,
    build_business_status,
    build_execution_period,
    build_task_from_event,
    build_workflow_tier_code,
    derive_task_status,
    generate_task_id,
)
from app.main import app


client = TestClient(app)


def make_event(**overrides: object) -> dict:
    event = {
        "event_id": "EVT-00001",
        "patient_id": "PT-98696",
        "workflow_tier": "Review",
        "escalation_state": "Completed",
        "signal_detected_time": "2026-09-27 23:29:17.888957",
        "action_initiated_time": "2026-09-27 23:51:17.888957",
        "action_completed_time": "2026-09-27 23:59:17.888957",
        "sla_target_min": 30,
        "sla_breached": False,
        "routing_attempts": 0,
        "data_quality_issue": "No Issue",
    }
    event.update(overrides)
    return event


def test_generate_task_id_is_deterministic() -> None:
    first = generate_task_id("EVT-00001")
    second = generate_task_id("EVT-00001")

    assert first == second
    assert first != generate_task_id("EVT-00002")


def test_derive_task_status_pending() -> None:
    event = make_event(
        escalation_state="Pending",
        action_initiated_time="",
        action_completed_time="",
    )

    assert derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
) == "requested"


def test_derive_task_status_acknowledged_without_action() -> None:
    event = make_event(
        escalation_state="Acknowledged",
        action_initiated_time="",
        action_completed_time="",
    )

    assert derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
) == "accepted"


def test_derive_task_status_acknowledged_with_action() -> None:
    event = make_event(
        escalation_state="Acknowledged",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="",
    )

    assert derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
) == "in-progress"


def test_derive_task_status_completed() -> None:
    event = make_event(
        escalation_state="Completed",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="2026-09-27 23:59:17.888957",
    )

    assert derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
) == "completed"


def test_pending_task_cannot_have_action_timestamps() -> None:
    event = make_event(
        escalation_state="Pending",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="",
    )

    with pytest.raises(ValueError, match="Pending"):
        derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
)


def test_completed_task_requires_completion_timestamp() -> None:
    event = make_event(
        escalation_state="Completed",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="",
    )

    with pytest.raises(ValueError, match="Completed"):
        derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
)


def test_unsupported_escalation_state_is_rejected() -> None:
    event = make_event(escalation_state="UnknownState")

    with pytest.raises(ValueError, match="Unsupported escalation state"):
        derive_task_status(
    event["escalation_state"],
    event["action_initiated_time"],
    event["action_completed_time"],
)


def test_execution_period_is_none_without_action_start() -> None:
    event = make_event(
        escalation_state="Acknowledged",
        action_initiated_time="",
        action_completed_time="",
    )

    task_status = derive_task_status(
        event["escalation_state"],
        event["action_initiated_time"],
        event["action_completed_time"],
    )

    assert build_execution_period(
        event["action_initiated_time"],
        event["action_completed_time"],
        task_status,
    ) is None


def test_execution_period_contains_start_for_in_progress_task() -> None:
    event = make_event(
        escalation_state="Acknowledged",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="",
    )

    period = build_execution_period(
    event["action_initiated_time"],
    event["action_completed_time"],
    derive_task_status(
        event["escalation_state"],
        event["action_initiated_time"],
        event["action_completed_time"],
    ),
)

    assert period is not None
    assert period.start == "2026-09-27T23:51:17.888957Z"
    assert period.end is None


def test_execution_period_contains_start_and_end_for_completed_task() -> None:
    event = make_event(
        escalation_state="Completed",
        action_initiated_time="2026-09-27 23:51:17.888957",
        action_completed_time="2026-09-27 23:59:17.888957",
    )

    period = build_execution_period(
    event["action_initiated_time"],
    event["action_completed_time"],
    derive_task_status(
        event["escalation_state"],
        event["action_initiated_time"],
        event["action_completed_time"],
    ),
)

    assert period is not None
    assert period.start == "2026-09-27T23:51:17.888957Z"
    assert period.end == "2026-09-27T23:59:17.888957Z"


def test_execution_period_rejects_end_before_start() -> None:
    event = make_event(
        action_initiated_time="2026-09-27 23:59:17.888957",
        action_completed_time="2026-09-27 23:51:17.888957",
    )

    with pytest.raises(ValueError, match="before"):
        build_execution_period(
    event["action_initiated_time"],
    event["action_completed_time"],
    derive_task_status(
        event["escalation_state"],
        event["action_initiated_time"],
        event["action_completed_time"],
    ),
)


def test_task_maps_observation_focus() -> None:
    task = build_task_from_event(make_event())

    assert task.focus is not None
    assert task.focus.reference == "Observation/EVT-00001-observation"


def test_task_maps_patient_reference() -> None:
    task = build_task_from_event(make_event())

    assert task.for_ is not None
    assert task.for_.reference == "Patient/PT-98696"


def test_task_maps_workflow_tier_to_code() -> None:
    code = build_workflow_tier_code("Review")

    assert code.text == "Review"
    assert len(code.coding) == 1
    assert code.coding[0].code == "review"
    assert code.coding[0].display == "Review"


def test_task_maps_escalation_state_to_business_status() -> None:
    business_status = build_business_status("Completed")

    assert business_status is not None
    assert business_status.text == "Completed"
    assert len(business_status.coding) == 1
    assert business_status.coding[0].code == "completed"


def test_task_does_not_use_priority_for_workflow_tier() -> None:
    task = build_task_from_event(make_event(workflow_tier="Activate"))

    assert not hasattr(task, "priority")


def test_task_does_not_include_sla_breach_or_routing_fields() -> None:
    task = build_task_from_event(
        make_event(
            sla_target_min=5,
            sla_breached=True,
            routing_attempts=3,
        )
    )

    serialized = task.model_dump(by_alias=True)

    assert "sla_target_min" not in serialized
    assert "sla_breached" not in serialized
    assert "routing_attempts" not in serialized


def test_task_completed_execution_period_has_end() -> None:
    task = build_task_from_event(make_event())

    assert task.status == "completed"
    assert task.executionPeriod is not None
    assert task.executionPeriod.start == "2026-09-27T23:51:17.888957Z"
    assert task.executionPeriod.end == "2026-09-27T23:59:17.888957Z"


def test_task_authored_on_maps_signal_detected_time() -> None:
    task = build_task_from_event(make_event())

    assert task.authoredOn == "2026-09-27T23:29:17.888957Z"


def test_task_sla_breach_does_not_map_to_failed() -> None:
    task = build_task_from_event(
        make_event(
            sla_breached=True,
            escalation_state="Completed",
        )
    )

    assert task.status == "completed"
    assert task.status != "failed"


def test_create_and_get_task() -> None:
    task = {
        "resourceType": "Task",
        "id": "e0e0c77b-0664-5e4e-84e1-5bf459b37b93",
        "identifier": [
            {
                "system": (
    "https://github.com/arapkirui513-hub/"
    "clinical-workflow-signal-audit/identifier/event-id"
),
                "value": "EVT-00001",
            }
        ],
        "status": "completed",
        "businessStatus": {
            "coding": [
                {
                    "system": (
    "https://github.com/arapkirui513-hub/"
    "clinical-workflow-signal-audit/CodeSystem/escalation-state"
),
                    "code": "completed",
                    "display": "Completed",
                }
            ],
            "text": "Completed",
        },
        "intent": "order",
        "code": {
            "coding": [
                {
                    "system": (
    "https://github.com/arapkirui513-hub/"
    "clinical-workflow-signal-audit/CodeSystem/workflow-tier"
),
                    "code": "review",
                    "display": "Review",
                }
            ],
            "text": "Review",
        },
        "focus": {
            "reference": "Observation/EVT-00001-observation",
        },
        "for": {
            "reference": "Patient/PT-98696",
        },
        "authoredOn": "2026-09-27T23:29:17.888957Z",
        "executionPeriod": {
            "start": "2026-09-27T23:51:17.888957Z",
            "end": "2026-09-27T23:59:17.888957Z",
        },
        "note": [
            {
                "text": (
                    "Synthetic operational task. No owner, requester, "
                    "or clinical order is implied."
                ),
            }
        ],
    }

    response = client.post("/fhir/Task", json=task)

    assert response.status_code == 201
    assert response.json() == task

    response = client.get(
        "/fhir/Task/e0e0c77b-0664-5e4e-84e1-5bf459b37b93"
    )

    assert response.status_code == 200
    assert response.json() == task


def test_task_not_found() -> None:
    response = client.get("/fhir/Task/does-not-exist")

    assert response.status_code == 404