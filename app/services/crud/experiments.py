from datetime import UTC, datetime

from app.services import schemas
from app.services.crud.linked_entities import get_experiments_not_linked_to_sample
from app.services.database import DbSession
from app.services.models import Experiment, LabSample, User


def get_user_experiments(
    db: DbSession, user: User, skip: int, limit: int
) -> list[Experiment]:
    if limit > 100:
        limit = 100
    is_archived = False
    return (
        db.query(Experiment)
        .filter(
            Experiment.user_id == user.id,
            Experiment.is_archived == is_archived,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user_experiment(
    db: DbSession,
    user: User,
    name: str,
    description: str,
    sample_families: list[str] | None = None,
) -> Experiment:
    now = datetime.now(tz=UTC)
    experiment = Experiment(
        user_id=user.id,
        created_at=now,
        updated_at=now,
        name=name,
        description=description,
    )

    if sample_families:
        samples = db.query(LabSample).filter(
            LabSample.user_id == user.id, LabSample.family.in_(sample_families)
        )
        for sample in samples:
            experiment.lab_samples.append(sample)

    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def get_user_experiment_by_id(
    db: DbSession, user: User, sample_id: int
) -> Experiment | None:
    return (
        db.query(Experiment)
        .filter(Experiment.id == sample_id, Experiment.user_id == user.id)
        .first()
    )


def edit_user_experiment_by_id(
    db: DbSession, user: User, experiment_id: int, experiment_data: schemas.Experiment
) -> bool:
    experiment = (
        db.query(Experiment)
        .filter(Experiment.id == experiment_id, Experiment.user_id == user.id)
        .first()
    )
    if experiment is None:
        return None
    experiment.name = experiment_data.name
    experiment.description = experiment_data.description
    experiment.updated_at = datetime.now(tz=UTC)
    db.commit()
    db.refresh(experiment)
    return experiment


def get_user_archived_experiments(db: DbSession, user: User) -> list[Experiment]:
    return (
        db.query(Experiment)
        .filter(Experiment.user_id == user.id, Experiment.is_archived)
        .all()
    )


def archive_user_experiment_by_id(
    db: DbSession,
    user: User,
    sample_id: int,
) -> bool | None:
    sample = (
        db.query(Experiment)
        .filter(Experiment.id == sample_id, Experiment.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    sample.is_archived = True
    db.commit()
    return True


def unarchive_user_experiment_by_id(
    db: DbSession, user: User, sample_id: int
) -> bool | None:
    sample = (
        db.query(Experiment)
        .filter(Experiment.id == sample_id, Experiment.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    sample.is_archived = False
    db.commit()
    return True


def delete_user_experiment_by_id(
    db: DbSession,
    user: User,
    sample_id: int,
) -> bool | None:
    sample = (
        db.query(Experiment)
        .filter(Experiment.id == sample_id, Experiment.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    db.delete(sample)
    db.commit()
    return True


def search_user_experiments(
    db: DbSession, user: User, search_term: str, exclude_sample_id: int | None = None
) -> list[Experiment]:
    if exclude_sample_id:
        return get_experiments_not_linked_to_sample(
            db, user, exclude_sample_id, search_term
        )

    if search_term.isdigit():
        return (
            db.query(Experiment)
            .filter(Experiment.id == search_term, Experiment.user_id == user.id)
            .all()
        )

    search_term = search_term.strip().lower()

    return (
        db.query(Experiment)
        .filter(
            Experiment.user_id == user.id,
            Experiment.name.ilike(f"%{search_term}%"),
        )
        .all()
    )
