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


def explain_misses(theory: str, misses: list[dict]) -> list[str] | None:
    if not misses:
        return []
    numbered = []
    for index, miss in enumerate(misses, start=1):
        numbered.append(
            f"{index}. Вопрос: {miss.get('prompt', '')}\n"
            f"Выбранный ответ: {miss.get('chosen', '')}\n"
            f"Верный ответ: {miss.get('correct', '')}"
        )
    content = complete(
        (
            "Ты объясняешь студенту ошибку в тесте по экономике. "
            "Для каждого пункта напиши 2-3 предложения: почему выбранный ответ неверен "
            "и почему верный следует из теории. Не добавляй факты, которых нет в теории. "
            "Без markdown, звёздочек и заголовков. "
            "Верни только JSON с полем explanations: список строк в том же порядке и той же длины."
        ),
        f"Теория:\n{theory}\n\nОшибки:\n" + "\n\n".join(numbered),
    )
    if content is None:
        return None
    try:
        return _parse_explanations(content, len(misses))
    except (KeyError, TypeError, ValueError):
        logger.warning("gigachat quiz explanation was not usable")
        return None


def generate_material(
    kind: str,
    slot_title: str,
    discipline_title: str,
    niche: str,
    tone: str,
    focuses: list[str] | None = None,
    question_count: int = 3,
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
            "Ты пишешь учебный блок по экономике для студента вуза. "
            "Сначала теория, потом ровно "
            f"{question_count} вопросов. "
            "Теория — развёрнутый конспект с заголовками markdown второго уровня. "
            "Четыре части, между частями пустая строка: "
            "что это такое; как применять, отдельным абзацем на каждый шаг; "
            "пример на каждую нишу, которая назначена вопросам; типичная ошибка. "
            "Объём теории не меньше 1500 знаков. "
            "У каждого вопроса ровно четыре варианта, и ровно один с isCorrect true. "
            "Верный вариант не ставь всегда первым. "
            "Каждый вопрос и каждый верный вариант должны следовать из теории. "
            "Нельзя спрашивать термин, пример, сравнение или вывод, которых в теории нет. "
            "Неверные варианты — правдоподобные ошибки про то же содержание, а не новые факты. "
            "У вопроса одна назначенная ниша или, реже, пара. Остальные интересы игрока не добавляй. "
            "Заголовки частей помечай только решётками markdown. "
            "Жирный, курсив, код и звёздочки не используй. "
            "Не повторяй инструкции, список назначений и слова «ниша игрока». "
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
        return _parse_material(kind, content, question_count)
    except (KeyError, TypeError, ValueError):
        logger.warning("gigachat material payload was not usable")
        return None


def _focus_plan(kind: str, focuses: list[str]) -> str:
    if kind == "boss":
        return f"Назначение кейса: {focuses[0]}."
    question_focuses = focuses[1:] or focuses
    covered = []
    for focus in question_focuses:
        for part in str(focus).split(" и "):
            label = part.strip()
            if label and label not in covered:
                covered.append(label)
    lines = [
        "Теория разбирает отдельный пример для каждой ниши вопросов: " + "; ".join(covered) + ".",
        *[f"Вопрос {index}: {focus}." for index, focus in enumerate(question_focuses, start=1)],
        "Вопрос проверяет только правила и пример теории для своей ниши.",
    ]
    return "Назначение, не включай эти строки в текст для студента:\n" + "\n".join(lines)


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


def _parse_explanations(content: str, count: int) -> list[str]:
    payload = _json_object(content)
    items = payload.get("explanations")
    if not isinstance(items, list) or len(items) < count:
        raise ValueError
    texts = []
    for item in items[:count]:
        if not isinstance(item, str) or not item.strip():
            raise ValueError
        texts.append(_clean_student_text(item))
    return texts


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


def _parse_material(kind: str, content: str, question_count: int = 3) -> dict:
    payload = _json_object(content)
    if kind == "boss":
        prompt = payload.get("promptMarkdown")
        if not isinstance(prompt, str) or len(prompt.strip()) < 80 or _is_instruction(prompt):
            raise ValueError
        return {"promptMarkdown": _clean_student_text(prompt)}
    theory = payload.get("theoryMarkdown")
    questions = payload.get("questions")
    if (
        not isinstance(theory, str)
        or len(theory.strip()) < 800
        or not isinstance(questions, list)
        or len(questions) < question_count
    ):
        raise ValueError
    if _is_instruction(theory):
        raise ValueError
    parsed = []
    for question in questions[:question_count]:
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
            parsed_options.append({"body": _clean_student_text(option["body"]), "isCorrect": is_correct})
        if correct != 1:
            raise ValueError
        parsed.append({"prompt": _clean_student_text(prompt), "options": parsed_options})
    return {"theoryMarkdown": _clean_student_text(theory), "questions": parsed}


def _strip_inline_markdown(text: str) -> str:
    cleaned = re.sub(r"`([^`]*)`", r"\1", text)
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"__(.+?)__", r"\1", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"(?<!\*)\*(?!\*)([^*\n]+)(?<!\*)\*(?!\*)", r"\1", cleaned)
    return cleaned.replace("**", "").replace("__", "").replace("`", "").replace("*", "")


def _clean_student_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        heading = re.match(r"^(\s{0,3}#{1,6}\s+)(.*)$", line)
        if heading:
            lines.append(heading.group(1) + _strip_inline_markdown(heading.group(2)).strip())
        else:
            lines.append(_strip_inline_markdown(line))
    return "\n".join(lines).strip()


def _is_instruction(text: str) -> bool:
    folded = text.casefold()
    markers = ("ниши игрока", "ниша игрока", "назначение ниш", "верни только json", "ты пишешь короткий")
    return any(marker in folded for marker in markers)


def _json_object(content: str) -> dict:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if match is None:
        raise ValueError
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError
    return payload
