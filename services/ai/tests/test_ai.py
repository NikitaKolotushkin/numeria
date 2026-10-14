import uuid

from fastapi.testclient import TestClient

from app.corpus import BLOCKS, BOSSES
from app.gigachat import _expiry
from app.main import app
from app.service import profiles

client = TestClient(app)
TOKEN = {"X-Service-Token": "dev-service-token"}


def setup_function():
    profiles.clear()


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
    assert body["theoryMarkdown"].startswith("Ниши игрока: спортивный клуб.")
    assert len(body["questions"]) == 3


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
    theory = opened.json()["theoryMarkdown"]
    assert "кинотеатр" in theory
    assert "книжный магазин" in theory


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
