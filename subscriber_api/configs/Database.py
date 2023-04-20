import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = "mysql://authuser:authuser@127.0.0.1:3306/testdb"

# Create Database Engine
Engine = create_engine(
    DATABASE_URL, echo=False, future=True
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=Engine
)


def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
