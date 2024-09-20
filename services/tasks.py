import csv

from services import schemas
from services.crud import create_user_experiment, create_user_sample
from services.database import DbSession
from services.models import User


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
