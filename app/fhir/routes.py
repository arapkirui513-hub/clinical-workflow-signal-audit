from app.fhir.task import FHIRTask
from fastapi import APIRouter, HTTPException

from app.fhir.observation import FHIRObservation
from app.fhir.patient import FHIRPatient

router = APIRouter(prefix="/fhir", tags=["FHIR"])

_patients: dict[str, FHIRPatient] = {}
_observations: dict[str, FHIRObservation] = {}
_tasks: dict[str, FHIRTask] = {}


@router.post(
    "/Patient",
    response_model=FHIRPatient,
    status_code=201,
)
def create_patient(
    patient: FHIRPatient,
) -> FHIRPatient:
    _patients[patient.id] = patient
    return patient


@router.get(
    "/Patient/{patient_id}",
    response_model=FHIRPatient,
)
def get_patient(
    patient_id: str,
) -> FHIRPatient:
    patient = _patients.get(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return patient


@router.post(
    "/Observation",
    response_model=FHIRObservation,
    status_code=201,
)
def create_observation(
    observation: FHIRObservation,
) -> FHIRObservation:
    _observations[observation.id] = observation
    return observation


@router.get(
    "/Observation/{observation_id}",
    response_model=FHIRObservation,
)
def get_observation(
    observation_id: str,
) -> FHIRObservation:
    observation = _observations.get(observation_id)

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail="Observation not found",
        )

    return observation


@router.post(
    "/Task",
    response_model=FHIRTask,
    status_code=201,
)
def create_task(
    task: FHIRTask,
) -> FHIRTask:
    _tasks[task.id] = task
    return task


@router.get(
    "/Task/{task_id}",
    response_model=FHIRTask,
)
def get_task(
    task_id: str,
) -> FHIRTask:
    task = _tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task