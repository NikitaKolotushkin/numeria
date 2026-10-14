import secrets

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.accounts import read_access
from app.config import settings
from app.db import get_db
from app.errors import ApiError

bearer = HTTPBearer(auto_error=False)


def require_service(x_service_token: str | None = Header(default=None)) -> None:
    if x_service_token is None or not secrets.compare_digest(x_service_token, settings.service_token):
        raise ApiError(401, "token_invalid", "Сессия недействительна")


def current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    user, jti, expires = read_access(db, credentials.credentials)
    return {"user": user, "jti": jti, "expires": expires, "db": db}
