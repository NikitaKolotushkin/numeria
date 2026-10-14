import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.deps import current_user, db_session, require_service, require_staff
from app.service import (
    admin_attempts,
    apply_retake,
    buildings_snapshot,
    open_block,
    open_boss,
    submit_block,
    submit_boss,
    track,
    user_progress,
)

router = APIRouter()


class AnswerIn(BaseModel):
    questionId: uuid.UUID
    optionId: uuid.UUID


class AttemptIn(BaseModel):
    answers: list[AnswerIn]


class BossAnswerIn(BaseModel):
    answerText: str


class RetakeIn(BaseModel):
    userId: uuid.UUID
    blockId: uuid.UUID
    sourceId: uuid.UUID


@router.get("/tracks/{building_id}")
def read_track(building_id: str, user=Depends(current_user), db: Session = Depends(db_session)):
    user_id, _role = user
    return track(db, user_id, building_id)


@router.get("/blocks/{block_id}")
def read_block(block_id: uuid.UUID, user=Depends(current_user), db: Session = Depends(db_session)):
    user_id, _role = user
    return open_block(db, user_id, block_id)


@router.post("/blocks/{block_id}/attempts")
def create_attempt(block_id: uuid.UUID, payload: AttemptIn, user=Depends(current_user), db: Session = Depends(db_session)):
    user_id, _role = user
    return submit_block(db, user_id, block_id, [answer.model_dump() for answer in payload.answers])


@router.get("/bosses/{boss_id}")
def read_boss(boss_id: uuid.UUID, user=Depends(current_user), db: Session = Depends(db_session)):
    user_id, _role = user
    return open_boss(db, user_id, boss_id)


@router.post("/bosses/{boss_id}/attempts")
def create_boss_attempt(
    boss_id: uuid.UUID,
    payload: BossAnswerIn,
    user=Depends(current_user),
    db: Session = Depends(db_session),
):
    user_id, _role = user
    return submit_boss(db, user_id, boss_id, payload.answerText)


@router.get("/me/progress")
def read_progress(user=Depends(current_user), db: Session = Depends(db_session)):
    user_id, _role = user
    return user_progress(db, user_id)


@router.get("/internal/players/{user_id}/buildings")
def read_player_buildings(user_id: uuid.UUID, _service=Depends(require_service), db: Session = Depends(db_session)):
    return buildings_snapshot(db, user_id)


@router.post("/internal/retake", status_code=204)
def retake(payload: RetakeIn, _service=Depends(require_service), db: Session = Depends(db_session)):
    apply_retake(db, payload.userId, payload.blockId, payload.sourceId)


@router.get("/admin/students/{user_id}/attempts")
def read_student_attempts(user_id: uuid.UUID, _staff=Depends(require_staff), db: Session = Depends(db_session)):
    return admin_attempts(db, user_id)
