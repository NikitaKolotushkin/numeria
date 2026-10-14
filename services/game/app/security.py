import secrets
import uuid

import jwt
from fastapi import Header

from app.config import settings
from app.errors import ApiError


def read_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise ApiError(401, "token_invalid", "Сессия недействительна")


def require_service_token(header: str | None) -> None:
    if header is None or not secrets.compare_digest(header, settings.service_token):
        raise ApiError(401, "token_invalid", "Сессия недействительна")
