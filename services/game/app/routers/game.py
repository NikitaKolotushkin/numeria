import uuid

from fastapi import APIRouter, Depends, Header, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.security import read_token, require_service_token
from app.service import apply_progress, create_player, leaderboard, state

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


class OnboardingAnswerIn(BaseModel):
    questionId: int
    optionIndex: int


class PlayerIn(BaseModel):
    userId: uuid.UUID
    onboardingAnswers: list[OnboardingAnswerIn] = []


class ProgressIn(BaseModel):
    userId: uuid.UUID
    reason: str
    sourceId: uuid.UUID
    buildingId: str
    passedSteps: int
    totalSteps: int
    currentTitle: str
    nextCondition: str


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> uuid.UUID:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    return read_token(credentials.credentials)


def service_token(x_service_token: str | None = Header(default=None)) -> None:
    require_service_token(x_service_token)


@router.get("/me/state")
def read_state(user_id: uuid.UUID = Depends(current_user), db: Session = Depends(get_db)):
    return state(db, user_id)


@router.get("/leaderboard")
def read_leaderboard(
    user_id: uuid.UUID = Depends(current_user),
    limit: int = Query(default=20),
    db: Session = Depends(get_db),
):
    return leaderboard(db, user_id, limit)


@router.post("/internal/players", status_code=204)
def open_player(payload: PlayerIn, _service=Depends(service_token), db: Session = Depends(get_db)):
    create_player(db, payload.userId, [item.model_dump() for item in payload.onboardingAnswers])


@router.post("/internal/progress", status_code=204)
def progress(payload: ProgressIn, _service=Depends(service_token), db: Session = Depends(get_db)):
    apply_progress(db, payload.model_dump())
