import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from app.deps import require_service
from app.errors import ApiError
from app.service import crisis_draft, ensure_profile, material, personalize, review

router = APIRouter(dependencies=[Depends(require_service)])


class PersonalizeIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: uuid.UUID = Field(alias="userId")
    hobbies: list[str] = []
    onboarding_answers: list[dict] = Field(default_factory=list, alias="onboardingAnswers")


class MaterialIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: uuid.UUID = Field(alias="userId")
    kind: str
    slot_title: str = Field(alias="slotTitle")
    discipline_title: str = Field(alias="disciplineTitle")
    niche: str = ""
    tone: str = ""


class ReviewIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: uuid.UUID = Field(alias="userId")
    boss_id: uuid.UUID = Field(alias="bossId")
    prompt_markdown: str = Field(alias="promptMarkdown")
    theory_markdown: str = Field(alias="theoryMarkdown")
    answer_text: str = Field(alias="answerText")
    pass_score: int = Field(alias="passScore")


class CrisisIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: uuid.UUID = Field(alias="userId")
    block_id: uuid.UUID = Field(alias="blockId")
    theory_markdown: str = Field(alias="theoryMarkdown")
    niche: str = ""
    tone: str = ""


@router.post("/internal/personalize")
def personalize_route(body: PersonalizeIn):
    return personalize(body.user_id, body.hobbies, body.onboarding_answers)


@router.post("/internal/material")
def material_route(body: MaterialIn):
    if body.kind not in {"block", "boss"}:
        raise ApiError(422, "validation_error", "Проверьте заполненные поля")
    return material(body.user_id, body.kind, body.slot_title, body.discipline_title)


@router.post("/internal/review")
def review_route(body: ReviewIn):
    if not body.answer_text.strip() or not body.prompt_markdown.strip():
        raise ApiError(422, "validation_error", "Проверьте заполненные поля")
    return review(body.user_id, body.prompt_markdown, body.theory_markdown, body.answer_text, body.pass_score)


@router.post("/internal/crisis-draft")
def crisis_route(body: CrisisIn):
    if not body.theory_markdown.strip():
        raise ApiError(422, "validation_error", "Проверьте заполненные поля")
    niche = ensure_profile(body.user_id).get("niche") or body.niche
    return crisis_draft(body.theory_markdown, niche)
