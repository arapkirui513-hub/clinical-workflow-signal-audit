from fastapi import APIRouter, HTTPException

from app.fhir.patient import FHIRPatient

router = APIRouter(prefix="/fhir", tags=["FHIR"])

_patients: dict[str, FHIRPatient] = {}


@router.post("/Patient", response_model=FHIRPatient, status_code=201)
def create_patient(patient: FHIRPatient) -> FHIRPatient:
    _patients[patient.id] = patient
    return patient


@router.get("/Patient/{patient_id}", response_model=FHIRPatient)
def get_patient(patient_id: str) -> FHIRPatient:
    patient = _patients.get(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient