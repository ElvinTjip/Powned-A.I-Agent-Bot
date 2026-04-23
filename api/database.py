import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base

_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
