from datetime import UTC, datetime

from fastapi import Depends, Request
from sqlalchemy import or_, text

from app.config import COOKIE_KEY
from app.services import schemas
from app.services.database import DbSession, get_db
from app.services.models import Experiment, LabSample, Measurement, User, UserSession
from app.services.security import hash_password, verify_password


def search_user(db: DbSession, search_term: str | int) -> list[User]:
    if isinstance(search_term, int):
        return db.query(User).filter(User.id == search_term).all()

    return db.query(User).filter(User.username.ilike(f"%{search_term}%")).all()


def get_user_by_username(db: DbSession, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_sessions(db: DbSession, user: User) -> UserSession:
    return db.query(UserSession).filter(UserSession.user_id == user.id)


def create_user_session(db: DbSession, user: User) -> UserSession:
    sessions = get_user_sessions(db, user)
    for session in sessions:
        db.delete(session)

    session = UserSession(
        user_id=user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def register_user_if_not_registered(db: DbSession, username: str, password: str):
    user = User(
        username=username,
        hashed_password=hash_password(password),
        created_at=datetime.now(tz=UTC),
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        return None


def login_user(db: DbSession, username: str, password: str) -> UserSession | None:
    user = get_user_by_username(db, username)
    if not user or not user.active:
        return None

    if not verify_password(user.hashed_password, password):
        return None

    return create_user_session(db, user)


def logout_user(db: DbSession, user: User) -> None:
    sessions = get_user_sessions(db, user)
    for session in sessions:
        db.delete(session)
    db.commit()


def get_current_user(request: Request, db: DbSession = Depends(get_db)) -> User | None:
    session_id = request.cookies.get(COOKIE_KEY)
    if not session_id:
        return None

    session = (
        db.query(UserSession).filter(UserSession.session_token == session_id).first()
    )
    if session is None:
        return None
    return session.user


def get_user_samples(
    db: DbSession, user: User, skip: int, limit: int
) -> list[LabSample]:
    if limit > 100:
        limit = 100
    is_archived = False
    samples = (
        db.query(LabSample)
        .filter(LabSample.user_id == user.id, LabSample.is_archived == is_archived)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return samples


def edit_user_sample_by_id(
    db: DbSession, user: User, sample_id: int, sample_data: schemas.LabSample
) -> bool:
    sample = (
        db.query(LabSample)
        .filter(LabSample.id == sample_id, LabSample.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    sample.label = sample_data.label
    sample.family = sample_data.family
    sample.format = sample_data.format
    sample.formula = sample_data.formula
    sample.updated_at = datetime.now(tz=UTC)
    db.commit()
    db.refresh(sample)
    return sample


def create_user_sample(
    db: DbSession,
    user: User,
    sample_data: schemas.LabSample,
) -> LabSample:
    now = datetime.now(tz=UTC)
    sample = LabSample(
        user_id=user.id,
        created_at=now,
        updated_at=now,
        **sample_data.model_dump(),
    )

    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


def get_user_sample_by_id(
    db: DbSession, user: User, sample_id: int
) -> LabSample | None:
    return (
        db.query(LabSample)
        .filter(LabSample.id == sample_id, LabSample.user_id == user.id)
        .first()
    )


def archive_user_sample_by_id(
    db: DbSession,
    user: User,
    sample_id: int,
) -> bool | None:
    sample = (
        db.query(LabSample)
        .filter(LabSample.id == sample_id, LabSample.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    sample.is_archived = True
    db.commit()
    return True


def unarchive_user_sample_by_id(
    db: DbSession, user: User, sample_id: int
) -> bool | None:
    sample = (
        db.query(LabSample)
        .filter(LabSample.id == sample_id, LabSample.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    sample.is_archived = False
    db.commit()
    return True


def get_user_archived_samples(db: DbSession, user: User) -> list[LabSample]:
    return (
        db.query(LabSample)
        .filter(LabSample.user_id == user.id, LabSample.is_archived)
        .all()
    )


def delete_user_sample_by_id(
    db: DbSession,
    user: User,
    sample_id: int,
) -> bool | None:
    sample = (
        db.query(LabSample)
        .filter(LabSample.id == sample_id, LabSample.user_id == user.id)
        .first()
    )
    if sample is None:
        return None
    db.delete(sample)
    db.commit()
    return True


def search_user_samples(db: DbSession, user: User, search_term: str) -> list[LabSample]:
    if search_term.isdigit():
        return (
            db.query(LabSample)
            .filter(LabSample.id == search_term, LabSample.user_id == user.id)
            .all()
        )

    search_term = search_term.strip().lower()

    return (
        db.query(LabSample)
        .filter(
            LabSample.user_id == user.id,
            or_(
                LabSample.label.ilike(f"%{search_term}%"),
                LabSample.family.ilike(f"%{search_term}%"),
                LabSample.format.ilike(f"%{search_term}%"),
                LabSample.formula.ilike(f"%{search_term}%"),
            ),
        )
        .all()
    )


def get_user_samples_by_family(
    db: DbSession, user: User, family: str
) -> list[LabSample]:
    return (
        db.query(LabSample)
        .filter(LabSample.user_id == user.id, LabSample.family == family)
        .all()
    )


def search_unique_lab_sample_families(
    db: DbSession, user: User, search_term: str
) -> list[str]:
    search_term = search_term.strip().lower()
    return (
        db.query(LabSample.family)
        .filter(
            LabSample.user_id == user.id, LabSample.family.ilike(f"%{search_term}%")
        )
        .distinct()
        .all()
    )


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


def get_user_sample_families(db: DbSession, user: User) -> list[str]:
    return (
        db.query(LabSample.family).filter(LabSample.user_id == user.id).distinct().all()
    )


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


def delete_all_user_archives(db: DbSession, user: User):
    samples = (
        db.query(LabSample)
        .filter(
            LabSample.user_id == user.id,
            LabSample.is_archived,
        )
        .all()
    )
    for sample in samples:
        db.delete(sample)

    experiments = (
        db.query(Experiment)
        .filter(
            Experiment.user_id == user.id,
            Experiment.is_archived,
        )
        .all()
    )
    for experiment in experiments:
        db.delete(experiment)

    db.commit()
    return True


def delete_all_user_entities(db: DbSession, user: User):
    samples = db.query(LabSample).filter(LabSample.user_id == user.id).all()
    for sample in samples:
        db.delete(sample)

    experiments = db.query(Experiment).filter(Experiment.user_id == user.id).all()
    for experiment in experiments:
        db.delete(experiment)

    measurements = db.query(Measurement).filter(Measurement.user_id == user.id).all()
    for measurement in measurements:
        db.delete(measurement)

    db.commit()
    return True


def get_user_archived_entity_summary(db: DbSession, user: User) -> tuple[str, str]:
    archived_samples_count = (
        db.query(LabSample)
        .filter(
            LabSample.user_id == user.id,
            LabSample.is_archived,
        )
        .count()
    )
    archived_experiments_count = (
        db.query(Experiment)
        .filter(
            Experiment.user_id == user.id,
            Experiment.is_archived,
        )
        .count()
    )
    return archived_samples_count, archived_experiments_count


def get_user_data_summary(db: DbSession, user: User) -> dict:
    samples_count = db.query(LabSample).filter(LabSample.user_id == user.id).count()
    experiments_count = (
        db.query(Experiment).filter(Experiment.user_id == user.id).count()
    )
    measurements_count = (
        db.query(Measurement)
        .join(LabSample)
        .filter(LabSample.user_id == user.id)
        .count()
    )
    return {
        "samples_count": samples_count,
        "experiments_count": experiments_count,
        "measurements_count": measurements_count,
        "storage_usage": calculate_storage_size_for_user(db, user.id),
    }


def get_user_measurements(
    db: DbSession, user: User, skip: int = 0, limit: int = 20
) -> list[Measurement]:
    if limit > 100:
        limit = 100
    return (
        db.query(Measurement)
        .filter(Measurement.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_measurement_by_id(db: DbSession, user: User, measurement_id: int):
    return (
        db.query(Measurement)
        .filter(
            Measurement.id == measurement_id,
            Measurement.user_id == user.id,
        )
        .first()
    )


def delete_user_measurement(
    db: DbSession, user: User, measurement_id: int
) -> bool | None:
    measurement = get_user_measurement_by_id(db, user, measurement_id)
    if measurement is None:
        return None
    db.delete(measurement)
    db.commit()
    return True


def create_user_measurement(
    db: DbSession, user: User, measurement_data: schemas.Measurements
):
    now = datetime.now(tz=UTC)
    measurement = Measurement(
        user_id=user.id,
        created_at=now,
        updated_at=now,
        **measurement_data.model_dump(),
    )
    db.add(measurement)
    db.commit()
    return measurement


def edit_user_measurement_by_id(
    db: DbSession, user: User, measurement_id: int, measurement_name: str
):
    measurement = (
        db.query(Measurement)
        .filter(Measurement.id == measurement_id, Measurement.user_id == user.id)
        .first()
    )
    if measurement is None:
        return None
    measurement.name = measurement_name
    measurement.updated_at = datetime.now(tz=UTC)
    db.commit()
    db.refresh(measurement)
    return measurement


def search_user_measurements(
    db: DbSession, user: User, search_term: str
) -> list[Measurement]:
    if search_term.isdigit():
        return (
            db.query(Measurement)
            .filter(Measurement.id == search_term, Measurement.user_id == user.id)
            .all()
        )

    search_term = search_term.strip().lower()

    return (
        db.query(Measurement)
        .filter(
            Measurement.user_id == user.id,
            or_(
                Measurement.name.ilike(f"%{search_term}%"),
            ),
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


def calculate_storage_size_for_user(db: DbSession, user_id: int) -> dict:
    counted_models = ["lab_samples", "experiments", "measurements"]

    select_statement = ", ".join(
        [
            f"COALESCE(SUM(pg_column_size({model})), 0) AS {model}_size"
            for model in counted_models
        ]
    )

    join_statement = " ".join(
        [f"LEFT JOIN {model} ON users.id = {model}.user_id" for model in counted_models]
    )
    query = text(f"""
    SELECT
        {select_statement}
    FROM users
    {join_statement}
    WHERE users.id = :user_id
    """)

    result = db.execute(query, {"user_id": user_id}).fetchone()
    return sum(result) / 1_048_576
