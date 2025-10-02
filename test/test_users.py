# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name

from fastapi import status

from patients_api.routers.users import get_db, get_current_user
from patients_api import main

from .utils import (
    override_get_current_user,
    override_get_db,
    test_user,
    client,
    TestingSessionLocal,
)

main.app.dependency_overrides[get_db] = override_get_db
main.app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    user_dict = {
        "id": 1,
        "email": "test@email.com",
        "username": "test",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "role": "admin",
        "phone_number": "1234567890"
    }

    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    for key, value in response_json.items():
        if key == "hashed_password":
            continue

        assert value == user_dict[key]


def test_change_password_success(test_user):
    response = client.put("/users/password", json={
        "old_password": "password",
        "new_password": "p@ssword"
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put("/users/password", json={
        "old_password": "badpass",
        "new_password": "p@ssword"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_phone_number_success(test_user):
    response = client.put("/users/phone-number", json={
        "phone_number": "1235551234",
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT
