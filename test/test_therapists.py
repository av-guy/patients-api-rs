# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name

from fastapi import status

from patients_api import main
from patients_api.routers.therapists import get_db, get_current_user
from patients_api.models import Therapist, Patient

from .utils import (
    override_get_current_user,
    override_get_db,
    client,
    test_therapist,
    test_patient,
    TestingSessionLocal
)


main.app.dependency_overrides[get_db] = override_get_db
main.app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_therapists(test_therapist):
    response = client.get("/therapists")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": test_therapist.id,
            "first_name": "Alice",
            "last_name": "Smith",
            "therapist_type": "PT",
        }
    ]


def test_read_therapists_by_name_and_type(test_therapist):
    response = client.get(
        "/therapists", params={"first_name": "Alice", "therapist_type": "PT"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"
    assert data[0]["therapist_type"] == "PT"


def test_create_therapist():
    request_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "therapist_type": "OT"
    }

    response = client.post("/therapists", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Therapist).filter(Therapist.first_name == "Bob").first()

    assert model is not None
    assert model.first_name == "Bob"
    assert model.last_name == "Johnson"
    assert model.therapist_type == "OT"


def test_list_therapist_patients(test_patient, test_therapist):
    db = TestingSessionLocal()

    patient = db.query(Patient).filter(Patient.id == test_patient.id).first()
    therapist = db.query(Therapist).filter(
        Therapist.id == test_therapist.id).first()

    patient.therapists.clear()
    db.commit()

    patient.therapists.append(therapist)
    db.commit()

    response = client.get(f"/therapists/{test_therapist.id}/patients")
    assert response.status_code == status.HTTP_200_OK

    patients = response.json()
    assert len(patients) == 1
    assert patients[0]["id"] == test_patient.id
    assert patients[0]["first_name"] == "John"


def test_update_therapist(test_therapist):
    request_data = {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast",
        "therapist_type": "SLP"
    }

    response = client.put(
        f"/therapists/{test_therapist.id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Therapist).filter(
        Therapist.id == test_therapist.id).first()

    assert model is not None
    assert model.first_name == "UpdatedFirst"
    assert model.last_name == "UpdatedLast"
    assert model.therapist_type == "SLP"

    assert model.patients == []


def test_delete_therapist(test_therapist):
    response = client.delete(f"/therapists/{test_therapist.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Therapist).filter(
        Therapist.id == test_therapist.id).first()

    assert model is None
