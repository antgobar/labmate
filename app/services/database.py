import time
import os

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import DATABASE_URL_KEY

DATABASE_URL = os.getenv(DATABASE_URL_KEY)

time.sleep(5)

engine = create_engine(url=DATABASE_URL, poolclass=pool.NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Session
