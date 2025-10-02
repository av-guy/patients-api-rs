import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost/PatientsDatabase"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

ENGINE = create_engine(SQLALCHEMY_DATABASE_URL)
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
BASE = declarative_base()
