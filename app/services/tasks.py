import csv
import os
from datetime import UTC, datetime

from app.config import ADMIN_USERNAME
from app.services import schemas
from app.services.crud import (
    create_user_experiment,
    create_user_sample,
    get_user_by_username,
)
from app.services.database import DbSession, SessionLocal
from app.services.models import User, UserRole
from app.services.security import hash_password


def populate_demo_data_on_registration(db: DbSession, user: User):
    experiment = create_user_experiment(
        db,
        user,
        "My First Experiment",
        "This is a demo experiment, have a look at the attached samples",
    )

    with open("static/csv/samples.csv") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            try:
                sample = create_user_sample(
                    db,
                    user,
                    schemas.LabSample(
                        formula=row[0], format=row[1], label=row[2], family=row[3]
                    ),
                )
                experiment.lab_samples.append(sample)
            except Exception:
                continue
        db.commit()


def create_admin_user() -> None:
    db = SessionLocal()
    admin_username = ADMIN_USERNAME
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        raise Exception(
            "Missing environment variable ADMIN_PASSWORD or ADMIN_PASSWORD_FILE"
        )

    hashed_password = hash_password(admin_password)
    user = get_user_by_username(db, admin_username)
    if user:
        user.hashed_password = hashed_password

    else:
        user = User(
            username=admin_username,
            hashed_password=hashed_password,
            role=UserRole.ADMIN.name,
            created_at=datetime.now(tz=UTC),
        )
        db.add(user)
    db.commit()
    db.close()
