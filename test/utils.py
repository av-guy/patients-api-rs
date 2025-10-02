# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from patients_api.database import BASE
from patients_api import main
from patients_api.models import Users, Patient, Therapist
from patients_api.routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

BASE.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "codingwithrobytest", "id": 1, "user_role": "admin"}


client = TestClient(main.app)


@pytest.fixture
def test_user():
    user = Users(
        email="test@email.com",
        username="test",
        first_name="John",
        last_name="Doe",
        hashed_password=bcrypt_context.hash("password"),
        is_active=True,
        role="admin",
        phone_number="1234567890"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture
def test_patient():
    patient = Patient(
        first_name="John",
        last_name="Doe"
    )

    db = TestingSessionLocal()
    db.add(patient)
    db.commit()

    yield patient

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM patients;"))
        connection.commit()


@pytest.fixture
def test_therapist():
    therapist = Therapist(
        first_name="Alice",
        last_name="Smith",
        therapist_type="PT"
    )

    db = TestingSessionLocal()
    db.add(therapist)
    db.commit()

    yield therapist

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM therapists;"))
        connection.commit()
