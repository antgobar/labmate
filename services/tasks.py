import csv
import os
from datetime import UTC, datetime

from config import ADMIN_PASSWORD_KEY, ADMIN_USERNAME
from services import schemas
from services.crud import (
    create_user_experiment,
    create_user_sample,
    get_user_by_username,
)
from services.database import DbSession, SessionLocal
from services.models import User, UserRole
from services.security import hash_password


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

    print(f"Demo data populated for user {user.id}")


def create_admin_user() -> None:
    db = SessionLocal()
    admin_username = ADMIN_USERNAME
    hashed_password = hash_password(os.getenv(ADMIN_PASSWORD_KEY))
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
