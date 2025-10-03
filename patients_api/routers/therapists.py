# pylint: disable=import-error
# pylint: disable=raise-missing-from

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from ..database import SESSION_LOCAL
from ..models import Therapist
from .auth import get_current_user


router = APIRouter(
    prefix="/therapists",
    tags=["therapists"]
)


def get_db():
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TherapistRequest(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    therapist_type: str = Field(min_length=2)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_therapists(
    user: user_dependency,
    db: db_dependency,
    first_name: str | None = None,
    last_name: str | None = None,
    therapist_type: str | None = None
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    query = db.query(Therapist)

    if first_name:
        query = query.filter(Therapist.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Therapist.last_name.ilike(f"%{last_name}%"))
    if therapist_type:
        query = query.filter(
            Therapist.therapist_type.ilike(f"%{therapist_type}%"))

    return query.all()


@router.get("/{therapist_id}/patients", status_code=status.HTTP_200_OK)
async def list_therapist_patients(
    user: user_dependency,
    db: db_dependency,
    therapist_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    therapist_model = db.query(Therapist).filter(
        Therapist.id == therapist_id).first()

    if not therapist_model:
        raise HTTPException(status_code=404, detail="Therapist not found")

    return therapist_model.patients


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_therapist(
    user: user_dependency,
    db: db_dependency,
    therapist_request: TherapistRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    therapist_model = Therapist(**therapist_request.model_dump())

    db.add(therapist_model)
    db.commit()
    db.refresh(therapist_model)

    return therapist_model


@router.put("/{therapist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_therapist(
    user: user_dependency,
    db: db_dependency,
    therapist_request: TherapistRequest,
    therapist_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    therapist_model = db.query(Therapist).filter(
        Therapist.id == therapist_id).first()

    if not therapist_model:
        raise HTTPException(status_code=404, detail="Therapist not found")

    try:
        therapist_model.first_name = therapist_request.first_name
        therapist_model.last_name = therapist_request.last_name
        therapist_model.therapist_type = therapist_request.therapist_type

        db.add(therapist_model)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")

    return


@router.delete("/{therapist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_therapist(
    user: user_dependency,
    db: db_dependency,
    therapist_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    therapist_model = db.query(Therapist).filter(
        Therapist.id == therapist_id).first()

    if not therapist_model:
        raise HTTPException(status_code=404, detail="Therapist not found")

    db.delete(therapist_model)
    db.commit()
    return
