# pylint: disable=import-error

from fastapi import FastAPI

from .routers import auth, users, patients, therapists
from .database import ENGINE
from .models import BASE


app = FastAPI()
BASE.metadata.create_all(bind=ENGINE)


@app.get("/healthy")
async def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(therapists.router)
