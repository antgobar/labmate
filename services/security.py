from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


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
    except VerifyMismatchError:
        return False
