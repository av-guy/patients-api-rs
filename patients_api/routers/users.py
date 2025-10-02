# pylint: disable=import-error

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SESSION_LOCAL
from ..models import Users
from .auth import get_current_user, bcrypt_context


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class PhoneNumberChangeRequest(BaseModel):
    phone_number: str


def get_db():
    db = SESSION_LOCAL()

    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    return current_user


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency, password_change_request: PasswordChangeRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if bcrypt_context.verify(password_change_request.old_password,
                             current_user.hashed_password):
        current_user.hashed_password = bcrypt_context.hash(
            password_change_request.old_password)
    else:
        raise HTTPException(
            status_code=401, detail="Old password does not match.")

    db.add(current_user)
    db.commit()


@router.put("/phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency,
    db: db_dependency,
    phone_change_request: PhoneNumberChangeRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    current_user.phone_number = phone_change_request.phone_number

    db.add(current_user)
    db.commit()
