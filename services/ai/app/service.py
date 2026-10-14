import json
import uuid
from pathlib import Path

import httpx

from app.config import settings
from app.corpus import (
    HOBBY_NICHE,
    block_material,
    boss_case,
    boss_material,
    content_focuses,
    niche_phrase,
    niches_for,
)
from app.errors import ApiError
from app.gigachat import generate_material, review_with_model

profiles: dict[uuid.UUID, dict] = {}


def load_profiles() -> None:
    path = _profile_file()
    if path is None or not path.exists():
        return
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        return
    for key, value in raw.items():
        if isinstance(value, dict):
            profiles[uuid.UUID(key)] = value


def personalize(user_id: uuid.UUID, hobbies: list[str], onboarding: list[dict]) -> dict:
    niches = niches_for([str(item) for item in hobbies])
    formal = [item for item in onboarding if isinstance(item, dict) and item.get("optionIndex", 0) >= 2]
    tone = "деловой" if len(formal) >= 3 else "конкретный"
    record = {"niches": niches, "niche": niche_phrase(niches), "tone": tone}
    profiles[user_id] = record
    _save_profiles()
    return {"niche": record["niche"], "niches": niches, "tone": tone}


def ensure_profile(user_id: uuid.UUID) -> dict:
    found = profiles.get(user_id)
    if found:
        return found
    remote = _fetch_choices(user_id)
    if remote is None:
        return {}
    return personalize(user_id, remote["hobbies"], remote["onboardingAnswers"])


def material(user_id: uuid.UUID, kind: str, slot_title: str, discipline_title: str) -> dict:
    profile = ensure_profile(user_id)
    niches = list(profile.get("niches") or [])
    if not niches and profile.get("niche"):
        niches = [profile["niche"]]
    parts = 4 if kind == "block" else 1
    focuses = content_focuses(niches, f"{kind}|{discipline_title}|{slot_title}", parts)
    generated = generate_material(
        kind,
        slot_title,
        discipline_title,
        profile.get("niche", ""),
        profile.get("tone", ""),
        focuses,
    )
    if generated is not None:
        return generated
    if kind == "boss":
        payload = boss_material(discipline_title)
    elif kind == "block":
        payload = block_material(discipline_title, slot_title)
    else:
        payload = None
    if payload is None:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    return _paint_focus(payload, focuses)


def _paint_focus(payload: dict, focuses: list[str]) -> dict:
    if not focuses:
        return payload
    if "promptMarkdown" in payload:
        return {**payload, "promptMarkdown": f"Дело: {focuses[0]}.\n\n{payload['promptMarkdown']}"}
    questions = []
    for index, question in enumerate(payload.get("questions") or []):
        focus = focuses[index + 1] if index + 1 < len(focuses) else focuses[0]
        questions.append({**question, "prompt": f"В деле «{focus}». {question['prompt']}"})
    return {
        **payload,
        "theoryMarkdown": f"Дело: {focuses[0]}.\n\n{payload['theoryMarkdown']}",
        "questions": questions,
    }


def review(user_id: uuid.UUID, prompt: str, theory: str, answer: str, pass_score: int) -> dict:
    profile = ensure_profile(user_id)
    model = review_with_model(prompt, theory, answer, profile.get("niche", ""))
    if model is not None:
        score = model["score"]
        verdict = "accepted" if score >= pass_score else "retry"
        return {**model, "verdict": verdict}
    return local_review(prompt, answer, pass_score)


def crisis_draft(theory: str, niche: str) -> dict:
    place = niche.strip() or "малый городской бизнес"
    return {
        "prompt": (
            f"В деле «{place}» за один день меняется условие из пройденного блока. "
            f"Опора для решения: {theory.strip()[:280]}"
        ),
        "options": [
            {"body": "Применить правило из пройденного блока к новому условию", "isCorrect": True},
            {"body": "Игнорировать условие и повторить вчерашнее решение", "isCorrect": False},
            {"body": "Выбрать вариант, который противоречит теории блока", "isCorrect": False},
            {"body": "Отложить решение без опоры на уже сданный материал", "isCorrect": False},
        ],
    }


def local_review(prompt: str, answer: str, pass_score: int) -> dict:
    folded = answer.lower().replace("ё", "е")
    case = boss_case(prompt)
    if case is None or len(folded.strip()) < 80:
        return {
            "score": 40,
            "verdict": "retry",
            "reviewText": "Пока не видно законченного решения: нужны опора на условие и вывод, что делать.",
            "growthZones": ["Законченное решение по условию"],
        }
    hits = []
    missed = []
    for check in case["checks"]:
        if any(needle in folded for needle in check["needles"]):
            hits.append(check["label"])
        else:
            missed.append(check["label"])
    score = round(100 * len(hits) / len(case["checks"]))
    if len(folded) < 80:
        score = min(score, 45)
    verdict = "accepted" if score >= pass_score else "retry"
    if hits and not missed:
        text = "В ответе есть " + _phrase(hits) + "."
        zones = [case["stretch"]]
    elif hits:
        text = "В ответе есть " + _phrase(hits) + ". Не хватает: " + _phrase(missed) + "."
        zones = missed[:3]
    else:
        text = "Пока не видно, " + _phrase(missed) + "."
        zones = missed[:3]
        score = min(score, 45)
        verdict = "retry"
    return {"score": score, "verdict": verdict, "reviewText": text, "growthZones": zones}


def _phrase(items: list[str]) -> str:
    lowered = [item[:1].lower() + item[1:] for item in items]
    if len(lowered) == 1:
        return lowered[0]
    return ", ".join(lowered[:-1]) + " и " + lowered[-1]


def known_hobbies() -> set[str]:
    return set(HOBBY_NICHE)


def _profile_file() -> Path | None:
    if not settings.profile_path.strip():
        return None
    return Path(settings.profile_path)


def _save_profiles() -> None:
    path = _profile_file()
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {str(user_id): record for user_id, record in profiles.items()}
    path.write_text(json.dumps(payload, ensure_ascii=False))


def _fetch_choices(user_id: uuid.UUID) -> dict | None:
    if not settings.users_base_url.strip():
        return None
    try:
        response = httpx.post(
            f"{settings.users_base_url.rstrip('/')}/internal/profiles",
            json={"userIds": [str(user_id)]},
            headers={"X-Service-Token": settings.service_token},
            timeout=2,
        )
    except httpx.HTTPError:
        return None
    if response.status_code != 200:
        return None
    for row in response.json().get("users", []):
        if row.get("userId") != str(user_id):
            continue
        return {
            "hobbies": row.get("hobbies") or [],
            "onboardingAnswers": row.get("onboardingAnswers") or [],
        }
    return None
