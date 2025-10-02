# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name

from fastapi import status

from patients_api import main
from patients_api.routers.patients import get_db, get_current_user
from patients_api.models import Patient

from .utils import (
    override_get_current_user,
    override_get_db,
    client,
    test_patient,
    test_therapist,
    TestingSessionLocal
)


main.app.dependency_overrides[get_db] = override_get_db
main.app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_patient):
    response = client.get("/patients")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
        }
    ]


def test_read_one_authenticated(test_patient):
    response = client.get("/patients/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe"
    }


def test_read_one_authenticated_not_found():
    response = client.get("/patients/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found"}


def test_create_patient():
    request_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "therapist_ids": []
    }

    response = client.post("/patients", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Patient).filter(Patient.id == 1).first()

    for key, value in request_data.items():
        if key == "therapist_ids":
            assert model.therapists == []
        else:
            assert getattr(model, key) == value


def test_update_patient(test_patient, test_therapist):
    request_data = {
        "therapists": [test_therapist.id]
    }

    response = client.put(f"/patients/{test_patient.id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Patient).filter(Patient.id == test_patient.id).first()

    assert model.first_name == "John"
    assert model.last_name == "Doe"
    assert len(model.therapists) == 1

    returned_therapist = model.therapists[0]
    assert returned_therapist.id == test_therapist.id


def test_delete_patient(test_patient):
    response = client.delete("/patients/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Patient).filter(Patient.id == 1).first()

    assert model is None


def test_update_patient_with_bad_therapist_id(test_patient):
    bad_id = 9999
    request_data = {
        "therapists": [bad_id]
    }

    response = client.put(f"/patients/{test_patient.id}", json=request_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "One or more therapists not found"}
