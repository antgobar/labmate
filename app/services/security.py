import os
import secrets

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app.services.schemas import AuthTokenPayload

_PASSWORD_LENGTH = 20
_JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def hash_password(password: str):
    ph = PasswordHasher()
    hash = ph.hash(password)
    if ph.check_needs_rehash(hash):
        raise Exception("Hash needs rehashing")
    return hash


def verify_password(hash, password: str):
    ph = PasswordHasher()
    try:
        ph.verify(hash, password)
        return not ph.check_needs_rehash(hash)
    except (VerifyMismatchError, InvalidHashError):
        return False


def hash_password_bcrypted(password: str):
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bytes, salt).decode("utf-8")


def verify_password_bcrypted(hashed_password: str, password: str):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def generate_random_password():
    return secrets.token_urlsafe(_PASSWORD_LENGTH)


def generate_auth_token(payload: AuthTokenPayload) -> str:
    return jwt.encode(payload.model_dump(), _JWT_SECRET_KEY, algorithm="HS256")


def decode_auth_token(token: str) -> AuthTokenPayload:
    payload = jwt.decode(token, _JWT_SECRET_KEY, algorithms=["HS256"])
    return AuthTokenPayload(**payload)
