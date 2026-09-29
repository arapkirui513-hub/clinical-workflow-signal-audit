from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


LOINC_SYSTEM = "http://loinc.org"

DATA_ABSENT_REASON_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/data-absent-reason"
)

CWS_BASE_URL = (
    "https://github.com/arapkirui513-hub/clinical-workflow-signal-audit"
)

RECORD_KIND_SYSTEM = (
    f"{CWS_BASE_URL}/CodeSystem/record-kind"
)

SIGNAL_TYPE_SYSTEM = (
    f"{CWS_BASE_URL}/CodeSystem/signal-type"
)

OBSERVATION_CATEGORY_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/observation-category"
)


SIGNAL_LOINC_CODES = {
    "Heart Rate": {
        "code": "8867-4",
        "display": "Heart rate",
        "local_code": "heart-rate",
    },
    "Respiratory Rate": {
        "code": "9279-1",
        "display": "Respiratory rate",
        "local_code": "respiratory-rate",
    },
    "Temperature": {
        "code": "8310-5",
        "display": "Body temperature",
        "local_code": "temperature",
    },
}


class FHIRCoding(BaseModel):
    system: str
    code: str
    display: str | None = None


class FHIRCodeableConcept(BaseModel):
    coding: list[FHIRCoding] = Field(default_factory=list)
    text: str | None = None


class FHIRReference(BaseModel):
    reference: str


class FHIRAnnotation(BaseModel):
    text: str


class FHIRObservation(BaseModel):
    resourceType: Literal["Observation"] = "Observation"

    id: str = Field(min_length=1)

    status: Literal[
        "registered",
        "preliminary",
        "final",
        "amended",
        "corrected",
        "cancelled",
        "entered-in-error",
        "unknown",
    ] = "unknown"

    category: list[FHIRCodeableConcept] = Field(
        default_factory=list
    )

    code: FHIRCodeableConcept

    subject: FHIRReference | None = None

    effectiveDateTime: str | None = None

    dataAbsentReason: FHIRCodeableConcept

    note: list[FHIRAnnotation] = Field(
        default_factory=list
    )


def build_observation_code(
    signal_type: str,
) -> FHIRCodeableConcept:
    mapping = SIGNAL_LOINC_CODES.get(signal_type)

    local_code = signal_type.lower().replace(" ", "-")

    coding = [
        FHIRCoding(
            system=SIGNAL_TYPE_SYSTEM,
            code=local_code,
            display=signal_type,
        )
    ]

    if mapping:
        coding.insert(
            0,
            FHIRCoding(
                system=LOINC_SYSTEM,
                code=mapping["code"],
                display=mapping["display"],
            ),
        )

    return FHIRCodeableConcept(
        coding=coding,
        text=signal_type,
    )


def format_fhir_datetime(value: str) -> str:
    """
    Format a naive source timestamp as a FHIR UTC dateTime.

    The synthetic dataset contains naive timestamps and the project
    convention interprets them as UTC.
    """

    source_datetime = datetime.fromisoformat(value)

    if source_datetime.tzinfo is not None:
        raise ValueError(
            "Expected a naive source datetime; "
            "FHIR export interprets source timestamps as UTC."
        )

    return source_datetime.isoformat(timespec="microseconds") + "Z"


def build_observation_from_event(
    event: dict,
) -> FHIRObservation:
    """
    Convert one synthetic workflow event into a FHIR Observation.

    The source dataset contains no clinical measurement values,
    so the resulting Observation deliberately contains no value[x].
    """

    signal_type = event["signal_type"]

    category = [
        FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system=RECORD_KIND_SYSTEM,
                    code="workflow-signal",
                    display="Workflow signal",
                )
            ],
            text="Workflow signal",
        )
    ]

    if signal_type in SIGNAL_LOINC_CODES:
        category.insert(
            0,
            FHIRCodeableConcept(
                coding=[
                    FHIRCoding(
                        system=OBSERVATION_CATEGORY_SYSTEM,
                        code="vital-signs",
                        display="Vital Signs",
                    )
                ],
                text="Vital Signs",
            ),
        )

    return FHIRObservation(
        id=f"{event['event_id']}-observation",
        status="unknown",
        category=category,
        code=build_observation_code(signal_type),
        subject=FHIRReference(
            reference=f"Patient/{event['patient_id']}",
        ),
        effectiveDateTime=format_fhir_datetime(
            str(event["signal_generated_time"])
        ),
        dataAbsentReason=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system=DATA_ABSENT_REASON_SYSTEM,
                    code="unsupported",
                    display="Unsupported",
                )
            ],
            text="Measurement value is not represented in the source dataset.",
        ),
        note=[
            FHIRAnnotation(
                text=(
                    "Synthetic workflow event. "
                    "Source dataset contains no measurement values."
                )
            )
        ],
    )