import secrets

from fastapi import Header

from app.config import settings
from app.errors import ApiError


def require_service(x_service_token: str | None = Header(default=None)) -> None:
    if x_service_token is None or not secrets.compare_digest(x_service_token, settings.service_token):
        raise ApiError(401, "token_invalid", "Сессия недействительна")
