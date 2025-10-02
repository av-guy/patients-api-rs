# pylint: disable=import-error
# pylint: disable=raise-missing-from

from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import SESSION_LOCAL
from ..models import Patient, Therapist

from .auth import get_current_user


router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)


def get_db():
    db = SESSION_LOCAL()

    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class PatientRequest(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    therapists: Optional[List[int]] = []


class TherapistAddRequest(BaseModel):
    therapists: Optional[List[int]] = []


@router.get("/", status_code=status.HTTP_200_OK)
async def read_patients(
    user: user_dependency,
    db: db_dependency,
    first_name: str | None = None,
    last_name: str | None = None
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    query = db.query(Patient)

    if first_name:
        query = query.filter(Patient.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Patient.last_name.ilike(f"%{last_name}%"))

    return query.all()


@router.get("/{patient_id}", status_code=status.HTTP_200_OK)
async def read_patient(
    user: user_dependency,
    db: db_dependency,
    patient_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    patient_model = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient_model:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient_model


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_patient(
    user: user_dependency,
    db: db_dependency,
    patient_request: PatientRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    patient_model = Patient(
        first_name=patient_request.first_name,
        last_name=patient_request.last_name,
    )

    if patient_request.therapists:
        therapists = (
            db.query(Therapist)
            .filter(Therapist.id.in_(patient_request.therapists))
            .all()
        )
        if len(therapists) != len(patient_request.therapists):
            raise HTTPException(
                status_code=404, detail="One or more therapists not found")

        patient_model.therapists.extend(therapists)

    db.add(patient_model)
    db.commit()
    db.refresh(patient_model)

    return patient_model


@router.put("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_patient(
    user: user_dependency,
    db: db_dependency,
    therapist_add_req: TherapistAddRequest,
    patient_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    patient_model = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient_model:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        patient_model.therapists.clear()

        if therapist_add_req.therapists:
            therapists = (
                db.query(Therapist)
                .filter(Therapist.id.in_(therapist_add_req.therapists))
                .all()
            )

            if len(therapists) != len(therapist_add_req.therapists):
                raise HTTPException(
                    status_code=404, detail="One or more therapists not found")

            patient_model.therapists.extend(therapists)

        db.add(patient_model)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")

    return


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    user: user_dependency,
    db: db_dependency,
    patient_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    patient_model = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient_model:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient_model)
    db.commit()
    return
