import logging

import httpx

from app.config import settings
from app.models import User

logger = logging.getLogger("numeria.users")


def notify_registered(user: User, hobbies: list[str], onboarding: list[dict]) -> None:
    calls = [
        (
            settings.game_base_url,
            "/internal/players",
            {"userId": str(user.id)},
        ),
        (
            settings.ai_base_url,
            "/internal/personalize",
            {
                "userId": str(user.id),
                "hobbies": hobbies,
                "onboardingAnswers": onboarding,
            },
        ),
        (
            settings.notifications_base_url,
            "/internal/welcome",
            {
                "userId": str(user.id),
                "email": user.email,
                "firstName": user.first_name,
            },
        ),
    ]
    headers = {"X-Service-Token": settings.service_token}
    for base_url, path, body in calls:
        if not base_url:
            continue
        try:
            httpx.post(
                f"{base_url.rstrip('/')}{path}",
                json=body,
                headers=headers,
                timeout=settings.downstream_timeout_seconds,
            )
        except httpx.HTTPError:
            logger.warning("downstream call failed: %s", path)
