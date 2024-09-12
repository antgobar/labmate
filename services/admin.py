import os
from datetime import UTC, datetime

from config import ADMIN_PASSWORD_KEY, ADMIN_USERNAME
from services.crud import get_user_by_username
from services.database import SessionLocal
from services.models import User, UserRole
from services.security import hash_password


def create_admin_user() -> None:
    db = SessionLocal()
    admin_username = ADMIN_USERNAME
    hashed_password = hash_password(os.getenv(ADMIN_PASSWORD_KEY))
    user = get_user_by_username(db, admin_username)
    if user:
        user.hashed_password = hashed_password
        return

    user = User(
        username=admin_username,
        hashed_password=hashed_password,
        role=UserRole.ADMIN.name,
        created_at=datetime.now(tz=UTC),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
