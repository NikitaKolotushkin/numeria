from fastapi import APIRouter, Depends

from app.accounts import patch_user, user_out
from app.deps import current_session
from app.schemas import PatchIn, UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
def read_me(session: dict = Depends(current_session)):
    return user_out(session["user"])


@router.patch("/me", response_model=UserOut)
def update_me(payload: PatchIn, session: dict = Depends(current_session)):
    return patch_user(session["db"], session["user"], payload)
