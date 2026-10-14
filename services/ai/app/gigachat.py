import json
import logging
import re
import uuid

import httpx

from app.config import settings

logger = logging.getLogger("numeria.ai")

_TOKEN: str | None = None


def review_with_model(prompt: str, theory: str, answer: str) -> dict | None:
    if not _credentials():
        return None
    try:
        token = _access_token()
        response = httpx.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": settings.gigachat_model,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты проверяешь открытый ответ студента экономического курса. "
                            "Оценивай логику решения и прикладную ценность. Не добавляй факты, которых нет в условии и теории. "
                            "Верни только JSON с полями score (целое 0-100), reviewText (короткий разбор) "
                            "и growthZones (список из одной-трёх коротких строк)."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Условие:\n{prompt}\n\nТеория:\n{theory}\n\nОтвет студента:\n{answer}",
                    },
                ],
            },
            timeout=settings.gigachat_timeout_seconds,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_review(content)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        logger.warning("gigachat review failed")
        return None


def _credentials() -> str:
    raw = settings.gigachat_credentials.strip()
    if len(raw) < 40 or raw.lower().startswith("your"):
        return ""
    return raw


def _access_token() -> str:
    global _TOKEN
    if _TOKEN:
        return _TOKEN
    response = httpx.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Authorization": f"Basic {_credentials()}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"scope": settings.gigachat_scope},
        timeout=settings.gigachat_timeout_seconds,
    )
    response.raise_for_status()
    _TOKEN = response.json()["access_token"]
    return _TOKEN


def _parse_review(content: str) -> dict:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if match is None:
        raise ValueError
    payload = json.loads(match.group(0))
    score = int(payload["score"])
    if score < 0 or score > 100:
        raise ValueError
    zones = payload["growthZones"]
    if not isinstance(zones, list) or not zones or not all(isinstance(item, str) and item.strip() for item in zones):
        raise ValueError
    text = payload["reviewText"]
    if not isinstance(text, str) or not text.strip():
        raise ValueError
    return {"score": score, "reviewText": text.strip(), "growthZones": [item.strip() for item in zones[:3]]}
