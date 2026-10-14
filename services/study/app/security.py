import uuid
from datetime import datetime, timezone

import jwt

from app.config import settings
from app.errors import ApiError


def read_token(token: str) -> tuple[uuid.UUID, str]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return uuid.UUID(payload["sub"]), str(payload["role"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise ApiError(401, "token_invalid", "Сессия недействительна")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
