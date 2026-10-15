import logging
import uuid

import httpx

from app.balance import FALLBACK_BUILDINGS
from app.config import settings

logger = logging.getLogger("numeria.game")


def study_buildings(user_id: uuid.UUID) -> list[dict]:
    if not settings.study_base_url:
        return fallback_buildings()
    try:
        response = httpx.get(
            f"{settings.study_base_url.rstrip('/')}/internal/players/{user_id}/buildings",
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.downstream_timeout_seconds,
        )
    except httpx.HTTPError:
        logger.warning("study buildings call failed")
        return fallback_buildings()
    if response.status_code != 200:
        return fallback_buildings()
    buildings = response.json().get("buildings")
    if not isinstance(buildings, list) or len(buildings) != 5:
        return fallback_buildings()
    return buildings


def user_onboarding(user_id: uuid.UUID) -> list[dict]:
    if not settings.users_base_url:
        return []
    try:
        response = httpx.post(
            f"{settings.users_base_url.rstrip('/')}/internal/profiles",
            json={"userIds": [str(user_id)]},
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.downstream_timeout_seconds,
        )
    except httpx.HTTPError:
        logger.warning("users onboarding call failed")
        return []
    if response.status_code != 200:
        return []
    for row in response.json().get("users", []):
        if row.get("userId") == str(user_id):
            answers = row.get("onboardingAnswers")
            return answers if isinstance(answers, list) else []
    return []


def user_names(user_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not user_ids or not settings.users_base_url:
        return {}
    try:
        response = httpx.post(
            f"{settings.users_base_url.rstrip('/')}/internal/profiles",
            json={"userIds": [str(user_id) for user_id in user_ids]},
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.downstream_timeout_seconds,
        )
    except httpx.HTTPError:
        logger.warning("users profiles call failed")
        return {}
    if response.status_code != 200:
        return {}
    names = {}
    for row in response.json().get("users", []):
        names[uuid.UUID(row["userId"])] = row["firstName"]
    return names


def fallback_buildings() -> list[dict]:
    return [
        {
            "buildingId": building_id,
            "passedSteps": 0,
            "totalSteps": total_steps,
            "currentTitle": title,
            "nextCondition": "Пройти теорию и тест",
        }
        for building_id, total_steps, title in FALLBACK_BUILDINGS
    ]
