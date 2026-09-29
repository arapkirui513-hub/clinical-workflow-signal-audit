from datetime import datetime
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field


CWS_BASE_URL = (
    "https://github.com/arapkirui513-hub/clinical-workflow-signal-audit"
)

IDENTIFIER_SYSTEM = (
    f"{CWS_BASE_URL}/identifier/event-id"
)

ESCALATION_STATE_SYSTEM = (
    f"{CWS_BASE_URL}/CodeSystem/escalation-state"
)

WORKFLOW_TIER_SYSTEM = (
    f"{CWS_BASE_URL}/CodeSystem/workflow-tier"
)


class FHIRIdentifier(BaseModel):
    system: str
    value: str


class FHIRCoding(BaseModel):
    system: str
    code: str
    display: str | None = None


class FHIRCodeableConcept(BaseModel):
    coding: list[FHIRCoding] = Field(
        default_factory=list
    )
    text: str | None = None


class FHIRReference(BaseModel):
    reference: str


class FHIRAnnotation(BaseModel):
    text: str


class FHIRPeriod(BaseModel):
    start: str | None = None
    end: str | None = None


class FHIRTask(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    resourceType: Literal["Task"] = "Task"

    id: str = Field(min_length=1)

    identifier: list[FHIRIdentifier] = Field(
        default_factory=list
    )

    status: Literal[
        "draft",
        "requested",
        "received",
        "accepted",
        "rejected",
        "ready",
        "cancelled",
        "in-progress",
        "on-hold",
        "failed",
        "completed",
        "entered-in-error",
    ]

    businessStatus: FHIRCodeableConcept | None = None

    intent: Literal[
        "proposal",
        "plan",
        "order",
        "original-order",
        "reflex-order",
        "filler-order",
        "instance-order",
        "option",
    ]

    code: FHIRCodeableConcept

    focus: FHIRReference | None = None

    for_: FHIRReference | None = Field(
        default=None,
        alias="for",
    )

    authoredOn: str | None = None

    executionPeriod: FHIRPeriod | None = None

    note: list[FHIRAnnotation] = Field(
        default_factory=list
    )


def generate_task_id(event_id: str) -> str:
    """
    Generate a deterministic UUIDv5 for a workflow Task.
    """

    return str(
        uuid5(
            NAMESPACE_URL,
            f"task:{event_id}",
        )
    )


def build_workflow_tier_code(
    workflow_tier: str,
) -> FHIRCodeableConcept:
    """
    Represent the project's workflow tier as a local
    Task code rather than FHIR priority.
    """

    local_code = workflow_tier.lower()

    return FHIRCodeableConcept(
        coding=[
            FHIRCoding(
                system=WORKFLOW_TIER_SYSTEM,
                code=local_code,
                display=workflow_tier,
            )
        ],
        text=workflow_tier,
    )


def build_business_status(
    escalation_state: str,
) -> FHIRCodeableConcept:
    """
    Preserve the source escalation state as Task.businessStatus.
    """

    return FHIRCodeableConcept(
        coding=[
            FHIRCoding(
                system=ESCALATION_STATE_SYSTEM,
                code=escalation_state.lower(),
                display=escalation_state,
            )
        ],
        text=escalation_state,
    )


def parse_source_datetime(
    value: str,
) -> datetime:
    """
    Parse a naive synthetic timestamp.

    The synthetic dataset does not contain timezone information.
    FHIR export treats these timestamps as UTC by project convention.
    """

    return datetime.fromisoformat(value)


def format_fhir_datetime(
    value: datetime,
) -> str:
    """
    Format a naive source timestamp as a FHIR UTC dateTime.

    The synthetic dataset contains naive timestamps and the project
    convention interprets them as UTC.
    """

    if value.tzinfo is not None:
        raise ValueError(
            "Expected a naive source datetime; "
            "FHIR export interprets source timestamps as UTC."
        )

    return value.isoformat(timespec="microseconds") + "Z"


def derive_task_status(
    escalation_state: str,
    action_initiated_time: str | None,
    action_completed_time: str | None,
) -> str:
    """
    Derive FHIR Task.status from the source workflow state
    and action timestamps.
    """

    if escalation_state == "Pending":
        if (
            action_initiated_time
            or action_completed_time
        ):
            raise ValueError(
                "Inconsistent workflow event: "
                "Pending event contains action timestamps."
            )

        return "requested"

    if escalation_state == "Acknowledged":
        if action_completed_time:
            raise ValueError(
                "Inconsistent workflow event: "
                "Acknowledged event contains an "
                "action_completed_time."
            )

        if action_initiated_time:
            return "in-progress"

        return "accepted"

    if escalation_state == "Completed":
        if not action_completed_time:
            raise ValueError(
                "Inconsistent workflow event: "
                "Completed event is missing "
                "action_completed_time."
            )

        return "completed"

    raise ValueError(
        f"Unsupported escalation state: {escalation_state}"
    )


def build_execution_period(
    action_initiated_time: str | None,
    action_completed_time: str | None,
    task_status: str,
) -> FHIRPeriod | None:
    """
    Map action timestamps to FHIR Task.executionPeriod.

    The end is emitted only for completed tasks.
    """

    if not action_initiated_time:
        return None

    start = parse_source_datetime(
        action_initiated_time
    )

    if task_status != "completed":
        return FHIRPeriod(
            start=format_fhir_datetime(start)
        )

    if not action_completed_time:
        raise ValueError(
            "Completed task requires action_completed_time."
        )

    end = parse_source_datetime(
        action_completed_time
    )

    if end < start:
        raise ValueError(
            "Invalid execution period: "
            "action_completed_time occurs before "
            "action_initiated_time."
        )

    return FHIRPeriod(
        start=format_fhir_datetime(start),
        end=format_fhir_datetime(end),
    )


def build_task_from_event(
    event: dict,
) -> FHIRTask:
    """
    Convert one synthetic workflow event into a FHIR Task.

    The Task represents operational work associated with
    the workflow signal. Clinical measurement data is not
    added to the Task.
    """

    event_id = str(event["event_id"])
    patient_id = str(event["patient_id"])

    escalation_state = str(
        event["escalation_state"]
    )

    action_initiated_time = event.get(
        "action_initiated_time"
    )

    action_completed_time = event.get(
        "action_completed_time"
    )

    if action_initiated_time is not None:
        action_initiated_time = str(
            action_initiated_time
        )

    if action_completed_time is not None:
        action_completed_time = str(
            action_completed_time
        )

    task_status = derive_task_status(
        escalation_state=escalation_state,
        action_initiated_time=action_initiated_time,
        action_completed_time=action_completed_time,
    )

    execution_period = build_execution_period(
        action_initiated_time=action_initiated_time,
        action_completed_time=action_completed_time,
        task_status=task_status,
    )

    authored_on = event.get(
        "signal_detected_time"
    )

    if authored_on is not None:
        authored_on = format_fhir_datetime(
            parse_source_datetime(str(authored_on))
        )

    return FHIRTask(
        id=generate_task_id(event_id),
        identifier=[
            FHIRIdentifier(
                system=IDENTIFIER_SYSTEM,
                value=event_id,
            )
        ],
        status=task_status,
        businessStatus=build_business_status(
            escalation_state
        ),
        intent="order",
        code=build_workflow_tier_code(
            str(event["workflow_tier"])
        ),
        focus=FHIRReference(
            reference=(
                f"Observation/"
                f"{event_id}-observation"
            )
        ),
        for_=FHIRReference(
            reference=f"Patient/{patient_id}"
        ),
        authoredOn=authored_on,
        executionPeriod=execution_period,
        note=[
            FHIRAnnotation(
                text=(
                    "Synthetic operational task. "
                    "No owner, requester, or clinical "
                    "order is implied."
                )
            )
        ],
    )
