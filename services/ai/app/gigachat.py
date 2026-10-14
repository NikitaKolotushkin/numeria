import json
import logging
import re
import time
import uuid

import httpx

from app.config import settings

logger = logging.getLogger("numeria.ai")

_TOKEN: str | None = None
_EXPIRES_AT = 0.0
_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def review_with_model(prompt: str, theory: str, answer: str, niche: str = "") -> dict | None:
    setting = (
        f"\nНиши игрока: {niche}. Их может быть от одной до шести. "
        "Условие использует одну или, реже, две. Оценивай ответ в мире условия "
        "и не требуй ниши, которых в тексте нет.\n"
        if niche.strip()
        else "\n"
    )
    content = complete(
        (
            "Ты проверяешь открытый ответ студента экономического курса. "
            "Оценивай логику решения и прикладную ценность. Не добавляй факты, которых нет в условии и теории. "
            "Верни только JSON с полями score (целое 0-100), reviewText (короткий разбор) "
            "и growthZones (список из одной-трёх коротких строк)."
        ),
        f"Условие:\n{prompt}\n\nТеория:\n{theory}{setting}\nОтвет студента:\n{answer}",
    )
    if content is None:
        return None
    try:
        return _parse_review(content)
    except (KeyError, TypeError, ValueError):
        logger.warning("gigachat review payload was not usable")
        return None


def generate_material(
    kind: str,
    slot_title: str,
    discipline_title: str,
    niche: str,
    tone: str,
    focuses: list[str] | None = None,
) -> dict | None:
    setting = niche.strip() or "малый городской бизнес"
    voice = tone.strip() or "конкретный"
    plan = _focus_plan(kind, focuses or [setting])
    if kind == "boss":
        system = (
            "Ты пишешь открытый бизнес-кейс уровня Junior для студента. "
            "Кейс опирается на учебную тему модуля и требует решения, а не определения. "
            "У игрока от одной до шести ниш. Весь текст происходит только в назначении: "
            "это одна ниша или, реже, пара. Остальные интересы не упоминай. "
            "Не выдумывай точные статистические цифры и названия реальных компаний. "
            "Верни только JSON с полем promptMarkdown: связный текст задания на русском, 4-7 предложений."
        )
        user = (
            f"Модуль: {discipline_title}. Тон: {voice}.\n{plan}"
        )
    elif kind == "block":
        system = (
            "Ты пишешь короткий учебный блок по экономике для студента вуза. "
            "Теория — два абзаца без списков. Затем ровно три вопроса. "
            "У каждого вопроса ровно четыре варианта, и ровно один с isCorrect true. "
            "Верный вариант не ставь всегда первым. "
            "У игрока от одной до шести ниш. У теории и у каждого вопроса своё назначение: "
            "одна ниша или, реже, пара. Варианты ответа остаются в этом назначении. "
            "Остальные интересы игрока в эту часть не добавляй. "
            "Учебные определения остаются верными. "
            "Не выдумывай точные статистические цифры и названия реальных компаний. "
            "Верни только JSON с полями theoryMarkdown и questions. "
            "Вопрос: prompt и options, вариант: body и isCorrect."
        )
        user = (
            f"Дисциплина: {discipline_title}. Слот: {slot_title}. Тон: {voice}.\n{plan}"
        )
    else:
        return None
    content = complete(system, user)
    if content is None:
        return None
    try:
        return _parse_material(kind, content)
    except (KeyError, TypeError, ValueError):
        logger.warning("gigachat material payload was not usable")
        return None


def _focus_plan(kind: str, focuses: list[str]) -> str:
    if kind == "boss":
        return f"Назначение кейса: {focuses[0]}."
    labels = ["Теория", "Вопрос 1", "Вопрос 2", "Вопрос 3"]
    lines = [f"{label}: {focus}." for label, focus in zip(labels, focuses)]
    return "Назначение ниш, не меняй его:\n" + "\n".join(lines)


def complete(system: str, user: str) -> str | None:
    if not _credentials():
        return None
    for attempt in range(2):
        try:
            token = _access_token(force=attempt == 1)
            response = httpx.post(
                _CHAT_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
                json={
                    "model": settings.gigachat_model,
                    "temperature": 0.4,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                timeout=settings.gigachat_timeout_seconds,
                verify=False,
            )
            if response.status_code == 401 and attempt == 0:
                continue
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
            logger.warning("gigachat call failed")
            if attempt == 1:
                return None
    return None


def _credentials() -> str:
    raw = settings.gigachat_credentials.strip()
    if len(raw) < 40 or raw.lower().startswith("your"):
        return ""
    return raw


def _access_token(force: bool = False) -> str:
    global _TOKEN, _EXPIRES_AT
    if not force and _TOKEN and time.time() < _EXPIRES_AT - 60:
        return _TOKEN
    response = httpx.post(
        _OAUTH_URL,
        headers={
            "Authorization": f"Basic {_credentials()}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={"scope": settings.gigachat_scope},
        timeout=settings.gigachat_timeout_seconds,
        verify=False,
    )
    response.raise_for_status()
    payload = response.json()
    _TOKEN = payload["access_token"]
    _EXPIRES_AT = _expiry(payload.get("expires_at"))
    return _TOKEN


def _expiry(raw) -> float:
    if isinstance(raw, (int, float)):
        return raw / 1000 if raw > 10_000_000_000 else float(raw)
    return time.time() + 25 * 60


def _parse_review(content: str) -> dict:
    payload = _json_object(content)
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


def _parse_material(kind: str, content: str) -> dict:
    payload = _json_object(content)
    if kind == "boss":
        prompt = payload.get("promptMarkdown")
        if not isinstance(prompt, str) or len(prompt.strip()) < 80:
            raise ValueError
        return {"promptMarkdown": prompt.strip()}
    theory = payload.get("theoryMarkdown")
    questions = payload.get("questions")
    if not isinstance(theory, str) or len(theory.strip()) < 80 or not isinstance(questions, list) or len(questions) < 1:
        raise ValueError
    parsed = []
    for question in questions[:3]:
        prompt = question.get("prompt") if isinstance(question, dict) else None
        options = question.get("options") if isinstance(question, dict) else None
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(options, list) or len(options) != 4:
            raise ValueError
        correct = 0
        parsed_options = []
        for option in options:
            if not isinstance(option, dict) or not isinstance(option.get("body"), str) or not option["body"].strip():
                raise ValueError
            is_correct = option.get("isCorrect") is True
            correct += int(is_correct)
            parsed_options.append({"body": option["body"].strip(), "isCorrect": is_correct})
        if correct != 1:
            raise ValueError
        parsed.append({"prompt": prompt.strip(), "options": parsed_options})
    return {"theoryMarkdown": theory.strip(), "questions": parsed}


def _json_object(content: str) -> dict:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if match is None:
        raise ValueError
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError
    return payload
