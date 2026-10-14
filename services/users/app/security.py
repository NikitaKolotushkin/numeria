import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

password_hasher = PasswordHash.recommended()
HOBBY_IDS = {"sport", "cinema", "music", "auto", "creativity", "books"}
ONBOARDING_QUESTIONS = {1, 2, 3, 4, 5}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def hash_refresh(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def encode_access(user_id: uuid.UUID, role: str, jti: uuid.UUID) -> str:
    expires = utcnow() + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "jti": str(jti),
            "exp": expires,
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


def decode_access(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
