from pydantic import BaseModel, Field

from app.fhir.observation import (
    FHIRObservation,
    FHIRReference as ObservationReference,
    build_observation_from_event,
)
from app.fhir.patient import FHIRPatient
from app.fhir.task import (
    FHIRTask,
    FHIRReference as TaskReference,
    build_task_from_event,
)


CWS_BASE_URL = (
    "https://github.com/arapkirui513-hub/clinical-workflow-signal-audit"
)


class FHIRWorkflowBundle(BaseModel):
    """
    Internal composition of the FHIR resources produced
    from one synthetic clinical workflow event.
    """

    patient: FHIRPatient
    observation: FHIRObservation
    task: FHIRTask


class FHIRBundleEntry(BaseModel):
    """
    One resource entry inside a FHIR Bundle.
    """

    fullUrl: str
    resource: FHIRPatient | FHIRObservation | FHIRTask


class FHIRBundle(BaseModel):
    """
    Standards-shaped FHIR Bundle containing the related
    Patient, Observation, and Task resources.
    """

    resourceType: str = "Bundle"
    type: str = "collection"
    entry: list[FHIRBundleEntry] = Field(default_factory=list)


def build_patient_from_event(
    event: dict,
) -> FHIRPatient:
    """
    Build the minimal Patient resource required by
    the workflow representation.

    The synthetic dataset does not provide demographic
    attributes, so only the patient identifier is mapped.
    """

    return FHIRPatient(
        id=str(event["patient_id"]),
    )


def build_workflow_bundle_from_event(
    event: dict,
) -> FHIRWorkflowBundle:
    """
    Convert one synthetic workflow event into its related
    Patient, Observation, and Task resources.
    """

    patient = build_patient_from_event(event)

    observation = build_observation_from_event(event)

    task = build_task_from_event(event)

    return FHIRWorkflowBundle(
        patient=patient,
        observation=observation,
        task=task,
    )


def build_fhir_bundle_from_event(
    event: dict,
) -> FHIRBundle:
    """
    Convert one synthetic workflow event into a FHIR
    collection Bundle.

    The standalone Patient, Observation, and Task builders
    retain their normal relative references. For the Bundle
    representation, those references are normalized to the
    corresponding Bundle entry fullUrl values.
    """

    workflow_bundle = build_workflow_bundle_from_event(event)

    patient = workflow_bundle.patient
    observation = workflow_bundle.observation
    task = workflow_bundle.task

    patient_url = (
        f"{CWS_BASE_URL}/Patient/{patient.id}"
    )

    observation_url = (
        f"{CWS_BASE_URL}/Observation/{observation.id}"
    )

    task_url = (
        f"{CWS_BASE_URL}/Task/{task.id}"
    )

    observation = observation.model_copy(
        deep=True,
        update={
            "subject": ObservationReference(
                reference=patient_url,
            )
        },
    )

    task = task.model_copy(
        deep=True,
        update={
            "focus": TaskReference(
                reference=observation_url,
            ),
            "for_": TaskReference(
                reference=patient_url,
            ),
        },
    )

    return FHIRBundle(
        entry=[
            FHIRBundleEntry(
                fullUrl=patient_url,
                resource=patient,
            ),
            FHIRBundleEntry(
                fullUrl=observation_url,
                resource=observation,
            ),
            FHIRBundleEntry(
                fullUrl=task_url,
                resource=task,
            ),
        ],
    )
