import logging
import uuid

import httpx

from app.config import settings
from app.errors import ApiError

logger = logging.getLogger("numeria.study")


def fetch_material(user_id: uuid.UUID, kind: str, slot_title: str, discipline_title: str) -> dict:
    return _post_ai(
        "/internal/material",
        {
            "userId": str(user_id),
            "kind": kind,
            "slotTitle": slot_title,
            "disciplineTitle": discipline_title,
            "niche": "",
            "tone": "",
        },
    )


def fetch_review(
    user_id: uuid.UUID,
    boss_id: uuid.UUID,
    prompt_markdown: str,
    theory_markdown: str,
    answer_text: str,
    pass_score: int,
) -> dict:
    return _post_ai(
        "/internal/review",
        {
            "userId": str(user_id),
            "bossId": str(boss_id),
            "promptMarkdown": prompt_markdown,
            "theoryMarkdown": theory_markdown,
            "answerText": answer_text,
            "passScore": pass_score,
        },
    )


def fetch_explanations(theory: str, misses: list[dict]) -> list[str] | None:
    try:
        payload = _post_ai(
            "/internal/quiz-explain",
            {"theoryMarkdown": theory, "misses": misses},
        )
    except ApiError:
        logger.warning("quiz explanation call failed")
        return None
    items = payload.get("explanations") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    return [item.strip() if isinstance(item, str) else "" for item in items]


def notify_game(body: dict) -> None:
    if not settings.game_base_url:
        return
    try:
        httpx.post(
            f"{settings.game_base_url.rstrip('/')}/internal/progress",
            json=body,
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.game_timeout_seconds,
        )
    except httpx.HTTPError:
        logger.warning("game progress call failed")


def _post_ai(path: str, body: dict) -> dict:
    if not settings.ai_base_url:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    try:
        response = httpx.post(
            f"{settings.ai_base_url.rstrip('/')}{path}",
            json=body,
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.ai_timeout_seconds,
        )
    except httpx.HTTPError:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    if response.status_code != 200:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    return response.json()
