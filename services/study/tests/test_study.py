import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

SECRET = "test-secret-key-with-enough-length"
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


def auth(role="student", user_id=None):
    user_id = user_id or uuid.uuid4()
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "jti": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        SECRET,
        algorithm="HS256",
    )
    return user_id, {"Authorization": f"Bearer {token}"}


def material(_user_id, kind, _slot_title, _discipline_title):
    if kind == "boss":
        return {"promptMarkdown": "Опишите решение."}
    return {
        "theoryMarkdown": "Теория блока.",
        "questions": [
            {
                "prompt": "Сколько будет 2 + 2?",
                "options": [
                    {"body": "3", "isCorrect": False},
                    {"body": "4", "isCorrect": True},
                    {"body": "5", "isCorrect": False},
                    {"body": "6", "isCorrect": False},
                ],
            }
        ],
    }


def test_track_starts_with_one_open_block(monkeypatch):
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.config import settings

    settings.jwt_secret = SECRET
    _user_id, headers = auth()
    response = client.get("/tracks/laboratory", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["moduleId"] == "analytics"
    assert len(body["steps"]) == 6
    assert body["steps"][0]["status"] == "available"
    assert body["steps"][0]["questionCount"] == 0
    assert body["steps"][1]["status"] == "locked"
    assert body["steps"][-1]["kind"] == "boss"
    assert body["steps"][-1]["status"] == "locked"
    assert body["bossUnlocked"] is False


def test_missing_snapshot_is_timeout(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    settings.ai_base_url = ""
    _user_id, headers = auth()
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    opened = client.get(f"/blocks/{block_id}", headers=headers)
    assert opened.status_code == 504
    assert opened.json()["error"]["code"] == "ai_timeout"


def test_quiz_pass_opens_next_block(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    calls = []
    explain_calls = []
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setattr("app.service.notify_game", lambda body: calls.append(body))
    monkeypatch.setattr(
        "app.service.fetch_explanations",
        lambda theory, misses: explain_calls.append(misses) or ["не должно вызваться"],
    )
    _user_id, headers = auth()
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    locked = client.get(f"/blocks/{track['steps'][1]['id']}", headers=headers)
    assert locked.status_code == 409
    opened = client.get(f"/blocks/{block_id}", headers=headers)
    assert opened.status_code == 200
    assert "isCorrect" not in opened.text
    question = opened.json()["questions"][0]
    correct = question["options"][1]["id"]
    submitted = client.post(
        f"/blocks/{block_id}/attempts",
        headers=headers,
        json={"answers": [{"questionId": question["id"], "optionId": correct}]},
    )
    assert submitted.status_code == 200
    assert submitted.json()["passed"] is True
    assert submitted.json()["score"] == 100
    assert submitted.json()["results"][0]["explanation"] == ""
    assert explain_calls == []
    again = client.get("/tracks/laboratory", headers=headers).json()
    assert again["steps"][0]["status"] == "passed"
    assert again["steps"][1]["status"] == "available"
    assert calls[0]["reason"] == "block_passed"
    assert calls[0]["passedSteps"] == 1


def test_failed_quiz_does_not_open_next(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setattr("app.service.notify_game", lambda body: None)
    monkeypatch.setattr(
        "app.service.fetch_explanations",
        lambda theory, misses: ["Среднее считают по всей выборке, а не по одной группе."],
    )
    _user_id, headers = auth()
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    opened = client.get(f"/blocks/{block_id}", headers=headers).json()
    wrong = opened["questions"][0]["options"][0]["id"]
    submitted = client.post(
        f"/blocks/{block_id}/attempts",
        headers=headers,
        json={"answers": [{"questionId": opened["questions"][0]["id"], "optionId": wrong}]},
    )
    body = submitted.json()
    assert body["passed"] is False
    assert body["score"] == 0
    assert body["results"][0]["questionId"] == opened["questions"][0]["id"]
    assert body["results"][0]["correctOptionId"] == opened["questions"][0]["options"][1]["id"]
    assert body["results"][0]["explanation"] == "Среднее считают по всей выборке, а не по одной группе."
    again = client.get("/tracks/laboratory", headers=headers).json()
    assert again["steps"][1]["status"] == "locked"


def test_failed_quiz_can_be_regenerated(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setattr("app.service.notify_game", lambda body: None)
    monkeypatch.setattr("app.service.fetch_explanations", lambda theory, misses: None)
    _user_id, headers = auth()
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    opened = client.get(f"/blocks/{block_id}", headers=headers).json()
    wrong = opened["questions"][0]["options"][0]["id"]
    client.post(
        f"/blocks/{block_id}/attempts",
        headers=headers,
        json={"answers": [{"questionId": opened["questions"][0]["id"], "optionId": wrong}]},
    )
    refreshed = client.post(f"/blocks/{block_id}/regenerate", headers=headers)
    assert refreshed.status_code == 200
    body = refreshed.json()
    assert body["theoryMarkdown"] == opened["theoryMarkdown"]
    assert body["questions"][0]["id"] != opened["questions"][0]["id"]
    assert "isCorrect" not in refreshed.text
    denied = client.post(f"/blocks/{track['steps'][1]['id']}/regenerate", headers=headers)
    assert denied.status_code == 409


def test_retake_is_idempotent(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    settings.service_token = "test-service-token"
    calls = []
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setattr("app.service.notify_game", lambda body: calls.append(body))
    user_id, headers = auth()
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    opened = client.get(f"/blocks/{block_id}", headers=headers).json()
    correct = opened["questions"][0]["options"][1]["id"]
    client.post(
        f"/blocks/{block_id}/attempts",
        headers=headers,
        json={"answers": [{"questionId": opened["questions"][0]["id"], "optionId": correct}]},
    )
    source_id = str(uuid.uuid4())
    payload = {"userId": str(user_id), "blockId": block_id, "sourceId": source_id}
    denied = client.post("/internal/retake", json=payload)
    assert denied.status_code == 401
    first = client.post("/internal/retake", json=payload, headers={"X-Service-Token": "test-service-token"})
    second = client.post("/internal/retake", json=payload, headers={"X-Service-Token": "test-service-token"})
    assert first.status_code == 204
    assert second.status_code == 204
    again = client.get("/tracks/laboratory", headers=headers).json()
    assert again["steps"][0]["status"] == "retake_required"
    assert again["bossUnlocked"] is False
    assert sum(1 for call in calls if call["reason"] == "retake_required") == 1


def test_admin_reads_answer_text(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    monkeypatch.setattr("app.service.fetch_material", material)
    monkeypatch.setattr("app.service.notify_game", lambda body: None)
    user_id, headers = auth()
    _staff_id, staff_headers = auth(role="curator")
    track = client.get("/tracks/laboratory", headers=headers).json()
    block_id = track["steps"][0]["id"]
    opened = client.get(f"/blocks/{block_id}", headers=headers).json()
    client.post(
        f"/blocks/{block_id}/attempts",
        headers=headers,
        json={"answers": [{"questionId": opened["questions"][0]["id"], "optionId": opened["questions"][0]["options"][1]["id"]}]},
    )
    forbidden = client.get(f"/admin/students/{user_id}/attempts", headers=headers)
    assert forbidden.status_code == 403
    visible = client.get(f"/admin/students/{user_id}/attempts", headers=staff_headers)
    assert visible.status_code == 200
    assert visible.json()["quizAttempts"][0]["answers"][0]["body"] == "4"


def test_unknown_building(monkeypatch):
    from app.config import settings

    settings.jwt_secret = SECRET
    _user_id, headers = auth()
    response = client.get("/tracks/hangar", headers=headers)
    assert response.status_code == 404
