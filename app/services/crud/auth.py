from datetime import UTC, datetime

from fastapi import Depends, Request

from app.config import COOKIE_KEY
from app.services.crud.user import get_user_by_username, get_user_sessions
from app.services.database import DbSession, get_db
from app.services.models import User, UserSession
from app.services.security import hash_password, verify_password


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
