from datetime import UTC, datetime

from sqlalchemy import or_

from app.services import schemas
from app.services.database import DbSession
from app.services.models import LabSample, User


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


def get_user_sample_families(db: DbSession, user: User) -> list[str]:
    return (
        db.query(LabSample.family).filter(LabSample.user_id == user.id).distinct().all()
    )
