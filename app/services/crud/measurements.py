from datetime import UTC, datetime

from sqlalchemy import or_

from app.services import schemas
from app.services.database import DbSession
from app.services.models import Measurement, User


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
