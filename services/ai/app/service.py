import uuid

from app.corpus import HOBBY_NICHE, block_material, boss_case, boss_material, niche_for
from app.errors import ApiError
from app.gigachat import review_with_model

profiles: dict[uuid.UUID, dict[str, str]] = {}


def personalize(user_id: uuid.UUID, hobbies: list[str], onboarding: list[dict]) -> dict:
    niche = niche_for([str(item) for item in hobbies])
    formal = [item for item in onboarding if isinstance(item, dict) and item.get("optionIndex", 0) >= 2]
    tone = "деловой" if len(formal) >= 3 else "конкретный"
    profiles[user_id] = {"niche": niche, "tone": tone}
    return {"niche": niche, "tone": tone}


def material(user_id: uuid.UUID, kind: str, slot_title: str, discipline_title: str) -> dict:
    if kind == "boss":
        payload = boss_material(discipline_title)
    elif kind == "block":
        payload = block_material(discipline_title, slot_title)
    else:
        payload = None
    if payload is None:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    if kind == "block":
        profile = profiles.get(user_id)
        if profile is not None:
            payload = {
                **payload,
                "theoryMarkdown": (
                    f"Ниша игрока: {profile['niche']}. Тот же материал можно примерять к этому делу.\n\n"
                    + payload["theoryMarkdown"]
                ),
            }
    return payload


def review(prompt: str, theory: str, answer: str, pass_score: int) -> dict:
    model = review_with_model(prompt, theory, answer)
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
