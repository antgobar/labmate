import os

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import DATABASE_URL_KEY


def construct_database_url():
    database_url = os.getenv(DATABASE_URL_KEY)
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER")
    password_file = os.getenv("POSTGRES_PASSWORD_FILE")
    with open(password_file) as file:
        password = file.read().strip()
    host = os.getenv("POSTGRES_HOST")
    database = os.getenv("POSTGRES_DB")
    if not all((user, password, host, database)):
        raise Exception("Missing environment variables for database connection")

    return f"postgresql://{user}:{password}@{host}/{database}"


DATABASE_URL = construct_database_url()

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
