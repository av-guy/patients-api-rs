from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# For development only: credentials are hardcoded here.
# In production, move the database URL to environment variables or a .env file
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/PatientsDatabase"
ENGINE = create_engine(SQLALCHEMY_DATABASE_URL)
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
BASE = declarative_base()
