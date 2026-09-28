from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_and_get_patient() -> None:
    patient = {
        "resourceType": "Patient",
        "id": "icu-001",
        "active": True,
        "gender": "unknown",
        "birthDate": "1980-01-01",
    }

    response = client.post("/fhir/Patient", json=patient)

    assert response.status_code == 201
    assert response.json() == patient

    response = client.get("/fhir/Patient/icu-001")

    assert response.status_code == 200
    assert response.json() == patient


def test_patient_not_found() -> None:
    response = client.get("/fhir/Patient/does-not-exist")

    assert response.status_code == 404