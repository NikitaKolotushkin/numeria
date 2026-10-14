import secrets
import uuid

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.errors import ApiError
from app.security import read_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> tuple[uuid.UUID, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    return read_token(credentials.credentials)


def require_staff(user: tuple[uuid.UUID, str] = Depends(current_user)) -> tuple[uuid.UUID, str]:
    _user_id, role = user
    if role not in {"curator", "admin"}:
        raise ApiError(403, "forbidden", "Недостаточно прав")
    return user


def require_service(x_service_token: str | None = Header(default=None)) -> None:
    if x_service_token is None or not secrets.compare_digest(x_service_token, settings.service_token):
        raise ApiError(401, "token_invalid", "Сессия недействительна")


def db_session(db: Session = Depends(get_db)) -> Session:
    return db
