import uuid

from fastapi.testclient import TestClient

from app.corpus import BLOCKS, BOSSES, content_focuses
from app.gigachat import _expiry
from app.main import app
from app.service import profiles

client = TestClient(app)
TOKEN = {"X-Service-Token": "dev-service-token"}


def setup_function():
    profiles.clear()


def test_quiz_explain_falls_back_without_model(monkeypatch):
    monkeypatch.setattr("app.service.explain_misses", lambda theory, misses: None)
    response = client.post(
        "/internal/quiz-explain",
        headers=TOKEN,
        json={
            "theoryMarkdown": "Среднее считают по всей выборке.",
            "misses": [{"prompt": "Что такое среднее?", "chosen": "одна группа", "correct": "вся выборка"}],
        },
    )
    assert response.status_code == 200
    text = response.json()["explanations"][0]
    assert "одна группа" in text
    assert "вся выборка" in text


def test_explain_parser_strips_marks():
    from app.gigachat import _parse_explanations

    assert _parse_explanations('{"explanations":["Это **среднее**."]}', 1) == ["Это среднее."]


def test_access_token_expiry_is_unix_seconds():
    assert _expiry(1_792_005_907_157) == 1_792_005_907.157
    assert _expiry(1_792_005_907) == 1_792_005_907


def test_material_requires_token():
    response = client.post("/internal/material", json={})
    assert response.status_code == 401


def test_every_block_has_one_correct_option():
    assert len(BLOCKS) == 30
    for item in BLOCKS.values():
        assert item["theory"].strip()
        assert len(item["questions"]) == 3
        for quiz in item["questions"]:
            assert len(quiz["options"]) == 4
            assert sum(option["isCorrect"] for option in quiz["options"]) == 1


def test_block_material_and_niche():
    user_id = str(uuid.uuid4())
    personal = client.post(
        "/internal/personalize",
        headers=TOKEN,
        json={"userId": user_id, "hobbies": ["sport"], "onboardingAnswers": []},
    )
    assert personal.status_code == 200
    assert personal.json()["niche"] == "спортивный клуб"
    opened = client.post(
        "/internal/material",
        headers=TOKEN,
        json={
            "userId": user_id,
            "kind": "block",
            "slotTitle": "Менеджмент, блок 2",
            "disciplineTitle": "Менеджмент",
            "niche": "",
            "tone": "",
        },
    )
    assert opened.status_code == 200
    body = opened.json()
    assert "Ниши игрока" not in body["theoryMarkdown"]
    assert body["theoryMarkdown"].strip()
    assert 5 <= len(body["questions"]) <= 10


def test_every_selected_hobby_reaches_the_material():
    user_id = str(uuid.uuid4())
    personal = client.post(
        "/internal/personalize",
        headers=TOKEN,
        json={"userId": user_id, "hobbies": ["cinema", "books"], "onboardingAnswers": []},
    )
    assert personal.status_code == 200
    assert personal.json()["niches"] == ["кинотеатр", "книжный магазин"]
    opened = client.post(
        "/internal/material",
        headers=TOKEN,
        json={
            "userId": user_id,
            "kind": "block",
            "slotTitle": "Маркетинг, блок 1",
            "disciplineTitle": "Маркетинг",
        },
    )
    assert opened.status_code == 200
    body = opened.json()
    text = body["theoryMarkdown"] + "\n" + "\n".join(question["prompt"] for question in body["questions"])
    assert "Ниши игрока" not in text
    assert "примерять" not in text


def _named(focus: str, niches: list[str]) -> list[str]:
    return [niche for niche in niches if niche in focus]


def test_one_hobby_fills_every_part():
    focuses = content_focuses(["спортивный клуб"], "Менеджмент, блок 2", 4)
    assert focuses == ["спортивный клуб"] * 4


def test_any_hobby_count_uses_one_niche_or_a_pair():
    samples = [
        ["автосервис", "книжный магазин"],
        ["спортивный клуб", "кинотеатр", "книжный магазин"],
        [
            "спортивный клуб",
            "кинотеатр",
            "музыкальная площадка",
            "автосервис",
            "творческая студия",
            "книжный магазин",
        ],
    ]
    for niches in samples:
        seen = set()
        pairs = 0
        for index in range(30):
            focuses = content_focuses(niches, f"Дисциплина, блок {index}", 4)
            pair_count = 0
            for focus in focuses:
                named = _named(focus, niches)
                assert 1 <= len(named) <= 2
                if len(named) == 2:
                    pair_count += 1
                    assert " и " in focus
                seen.update(named)
            assert pair_count <= 1
            if pair_count:
                pairs += 1
        assert seen == set(niches)
        assert pairs < 12


def test_boss_review_accepts_a_full_answer():
    case = BOSSES["Основы и введение"]
    answer = (
        "Вместе с задачей сотруднику нужно передать полномочия запрашивать цифры у соседнего отдела. "
        "Сотрудник собирает отчёт в пределах этих прав. Ответственность за итог и за срок остаётся у руководителя: "
        "без прав сотрудник задачу не закроет."
    )
    response = client.post(
        "/internal/review",
        headers=TOKEN,
        json={
            "userId": str(uuid.uuid4()),
            "bossId": str(uuid.uuid4()),
            "promptMarkdown": case["prompt"],
            "theoryMarkdown": "Делегирование передаёт права.",
            "answerText": answer,
            "passScore": 70,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["score"] >= 70
    assert body["verdict"] == "accepted"
    assert body["reviewText"]
    assert body["growthZones"]


def test_short_boss_answer_is_retry():
    case = BOSSES["Основы и введение"]
    response = client.post(
        "/internal/review",
        headers=TOKEN,
        json={
            "userId": str(uuid.uuid4()),
            "bossId": str(uuid.uuid4()),
            "promptMarkdown": case["prompt"],
            "theoryMarkdown": "Теория.",
            "answerText": "Надо сделать отчёт",
            "passScore": 70,
        },
    )
    assert response.status_code == 200
    assert response.json()["verdict"] == "retry"
    assert response.json()["score"] < 70
