import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.main import app

SECRET = "test-secret-key-with-enough-length"
settings.jwt_secret = SECRET
settings.service_token = "test-service-token"
settings.study_base_url = ""
settings.users_base_url = ""

engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)
SERVICE = {"X-Service-Token": "test-service-token"}


def auth(user_id=None):
    user_id = user_id or uuid.uuid4()
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": "student",
            "jti": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        SECRET,
        algorithm="HS256",
    )
    return user_id, {"Authorization": f"Bearer {token}"}


def progress(user_id, reason, building_id="accounting", passed=1, total=4):
    return {
        "userId": str(user_id),
        "reason": reason,
        "sourceId": str(uuid.uuid4()),
        "buildingId": building_id,
        "passedSteps": passed,
        "totalSteps": total,
        "currentTitle": "Бухгалтерский учет, блок 2",
        "nextCondition": "Пройти теорию и тест",
    }


def test_player_starts_at_level_one():
    user_id, headers = auth()
    created = client.post("/internal/players", json={"userId": str(user_id)}, headers=SERVICE)
    assert created.status_code == 204
    again = client.post("/internal/players", json={"userId": str(user_id)}, headers=SERVICE)
    assert again.status_code == 204
    body = client.get("/me/state", headers=headers).json()
    assert body["capital"] == 0
    assert body["xp"] == 0
    assert body["readiness"] == ""
    assert body["rankPosition"] == 1
    accounting = next(item for item in body["buildings"] if item["buildingId"] == "accounting")
    assert accounting["level"] == 1
    assert accounting["totalSteps"] == 4
    assert accounting["mastery"] == "0 / 4"


def test_passed_block_raises_level_without_using_coins_for_it():
    user_id, headers = auth()
    client.post("/internal/players", json={"userId": str(user_id)}, headers=SERVICE)
    payload = progress(user_id, "block_passed", passed=1, total=4)
    assert client.post("/internal/progress", json=payload, headers=SERVICE).status_code == 204
    assert client.post("/internal/progress", json=payload, headers=SERVICE).status_code == 204
    body = client.get("/me/state", headers=headers).json()
    assert body["capital"] == 100
    assert body["xp"] == 10
    accounting = next(item for item in body["buildings"] if item["buildingId"] == "accounting")
    assert accounting["level"] == 2
    assert accounting["passedSteps"] == 1
    office = next(item for item in body["buildings"] if item["buildingId"] == "office")
    assert office["level"] == 1


def test_coins_order_the_leaderboard_and_crisis_does_not_drop_level():
    rich_id, rich_headers = auth()
    poor_id, _poor_headers = auth()
    client.post("/internal/players", json={"userId": str(rich_id)}, headers=SERVICE)
    client.post("/internal/players", json={"userId": str(poor_id)}, headers=SERVICE)
    client.post("/internal/progress", json=progress(rich_id, "boss_passed", passed=4, total=4), headers=SERVICE)
    client.post("/internal/progress", json=progress(poor_id, "block_passed", passed=1, total=4), headers=SERVICE)
    board = client.get("/leaderboard", headers=rich_headers).json()["players"]
    assert board[0]["capital"] == 400
    assert board[1]["capital"] == 100
    before = client.get("/me/state", headers=rich_headers).json()
    level_before = next(item["level"] for item in before["buildings"] if item["buildingId"] == "accounting")
    client.post(
        "/internal/progress",
        json=progress(rich_id, "crisis_failed", passed=4, total=4),
        headers=SERVICE,
    )
    after = client.get("/me/state", headers=rich_headers).json()
    level_after = next(item["level"] for item in after["buildings"] if item["buildingId"] == "accounting")
    assert after["capital"] == 350
    assert level_after == level_before == 5


def test_retake_lowers_level_and_keeps_coins():
    user_id, headers = auth()
    client.post("/internal/players", json={"userId": str(user_id)}, headers=SERVICE)
    client.post("/internal/progress", json=progress(user_id, "block_passed", passed=1, total=4), headers=SERVICE)
    client.post(
        "/internal/progress",
        json=progress(user_id, "retake_required", passed=0, total=4),
        headers=SERVICE,
    )
    body = client.get("/me/state", headers=headers).json()
    accounting = next(item for item in body["buildings"] if item["buildingId"] == "accounting")
    assert body["capital"] == 100
    assert accounting["level"] == 1
    assert accounting["passedSteps"] == 0


def test_registration_quiz_sets_readiness_without_raising_buildings():
    user_id, headers = auth()
    perfect = [
        {"questionId": 1, "optionIndex": 2},
        {"questionId": 2, "optionIndex": 1},
        {"questionId": 3, "optionIndex": 1},
        {"questionId": 4, "optionIndex": 2},
        {"questionId": 5, "optionIndex": 1},
    ]
    created = client.post(
        "/internal/players",
        json={"userId": str(user_id), "onboardingAnswers": perfect},
        headers=SERVICE,
    )
    assert created.status_code == 204
    body = client.get("/me/state", headers=headers).json()
    assert body["readiness"] == "Подготовленный"
    assert body["capital"] == 0
    assert all(item["level"] == 1 for item in body["buildings"])

    missed = perfect.copy()
    missed[0] = {"questionId": 1, "optionIndex": 0}
    other, other_headers = auth()
    client.post(
        "/internal/players",
        json={"userId": str(other), "onboardingAnswers": missed},
        headers=SERVICE,
    )
    assert client.get("/me/state", headers=other_headers).json()["readiness"] == "Уверенный"
