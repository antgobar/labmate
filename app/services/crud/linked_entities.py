from datetime import UTC, datetime

from app.services import schemas
from app.services.database import DbSession
from app.services.models import Experiment, LabSample, Measurement, User


def add_measurements_to_user_sample(
    db: DbSession, user: User, sample_id: int, measurement_data: schemas.Measurements
):
    measurement = Measurement(
        user_id=user.id,
        lab_sample_id=sample_id,
        created_at=datetime.now(tz=UTC),
        **measurement_data.model_dump(),
    )
    db.add(measurement)
    db.commit()
    return measurement


def get_experiments_not_linked_to_sample(
    db: DbSession, user: User, sample_id: int, search_term: str
) -> list[Experiment]:
    if search_term.isdigit():
        return (
            db.query(Experiment).filter(
                Experiment.id == search_term, Experiment.user_id == user.id
            ),
            ~Experiment.lab_samples.any(LabSample.id == sample_id).all(),
        )

    return (
        db.query(Experiment)
        .filter(
            Experiment.user_id == user.id,
            ~Experiment.lab_samples.any(LabSample.id == sample_id),
            Experiment.name.ilike(f"%{search_term}%"),
        )
        .all()
    )


def link_sample_and_experiment(
    db: DbSession, user: User, experiment_id: int, sample_id: int
) -> tuple[Experiment, LabSample] | tuple[None, None]:
    experiment = (
        db.query(Experiment)
        .filter(
            Experiment.id == experiment_id,
            Experiment.user_id == user.id,
        )
        .first()
    )
    sample = (
        db.query(LabSample)
        .filter(
            LabSample.id == sample_id,
            LabSample.user_id == user.id,
        )
        .first()
    )
    if experiment is None or sample is None:
        return None, None
    if sample not in experiment.lab_samples:
        experiment.lab_samples.append(sample)
        db.commit()
    return experiment, sample


def unlink_sample_and_experiment(
    db: DbSession, user: User, experiment_id: int, sample_id: int
) -> tuple[Experiment, LabSample] | tuple[None, None]:
    experiment = (
        db.query(Experiment)
        .filter(
            Experiment.id == experiment_id,
            Experiment.user_id == user.id,
        )
        .first()
    )
    sample = (
        db.query(LabSample)
        .filter(
            LabSample.id == sample_id,
            LabSample.user_id == user.id,
        )
        .first()
    )
    if experiment is None or sample is None or sample not in experiment.lab_samples:
        return None, None
    experiment.lab_samples.remove(sample)
    db.commit()
    return experiment, sample
