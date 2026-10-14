from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.accounts import login_user, logout_user, register_user, rotate_refresh
from app.db import get_db
from app.deps import current_session
from app.downstream import notify_registered
from app.schemas import AuthOut, LoginIn, RefreshIn, RegisterIn
from app.validation import validate_register

router = APIRouter()


@router.post("/auth/register", response_model=AuthOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    checked = validate_register(payload)
    user, session = register_user(db, checked)
    notify_registered(
        user,
        checked.hobbies,
        [
            {"questionId": answer.question_id, "optionIndex": answer.option_index}
            for answer in checked.onboarding_answers
        ],
    )
    return session


@router.post("/auth/login", response_model=AuthOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    return login_user(db, payload.email, payload.password)


@router.post("/auth/refresh", response_model=AuthOut)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)):
    return rotate_refresh(db, payload.refresh_token)


@router.post("/auth/logout", status_code=204)
def logout(payload: RefreshIn, session: dict = Depends(current_session)):
    logout_user(session["db"], session["user"], session["jti"], session["expires"], payload.refresh_token)
    return Response(status_code=204)
