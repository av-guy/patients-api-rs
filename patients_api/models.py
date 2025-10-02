
# pylint: disable=too-few-public-methods

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from .database import BASE


class Users(BASE):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


patient_therapist = Table(
    "patient_therapist",
    BASE.metadata,
    Column("patient_id", Integer, ForeignKey("patients.id"), primary_key=True),
    Column("therapist_id", Integer, ForeignKey(
        "therapists.id"), primary_key=True),
)


class Patient(BASE):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)

    therapists = relationship(
        "Therapist",
        secondary=patient_therapist,
        back_populates="patients"
    )


class Therapist(BASE):
    __tablename__ = "therapists"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    therapist_type = Column(String)

    patients = relationship(
        "Patient",
        secondary=patient_therapist,
        back_populates="therapists"
    )
