import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_service
from app.models import User

router = APIRouter()


class ProfilesIn(BaseModel):
    userIds: list[uuid.UUID]


@router.post("/internal/profiles")
def profiles(payload: ProfilesIn, _service=Depends(require_service), db: Session = Depends(get_db)):
    if not payload.userIds:
        return {"users": []}
    rows = db.scalars(select(User).where(User.id.in_(payload.userIds))).all()
    return {"users": [{"userId": str(row.id), "firstName": row.first_name} for row in rows]}
