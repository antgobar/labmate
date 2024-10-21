from sqlalchemy import text

from app.services.database import DbSession
from app.services.models import Experiment, LabSample, Measurement, User, UserSession


def search_user(db: DbSession, search_term: str | int) -> list[User]:
    if isinstance(search_term, int):
        return db.query(User).filter(User.id == search_term).all()

    return db.query(User).filter(User.username.ilike(f"%{search_term}%")).all()


def get_user_by_username(db: DbSession, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_sessions(db: DbSession, user: User) -> UserSession:
    return db.query(UserSession).filter(UserSession.user_id == user.id)


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
