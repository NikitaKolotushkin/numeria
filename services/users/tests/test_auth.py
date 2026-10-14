import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

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


def answers():
    return [{"questionId": number, "optionIndex": 0} for number in range(1, 6)]


def register_body(**overrides):
    body = {
        "firstName": "Данил",
        "lastName": "Зенин",
        "university": "ГУУ",
        "direction": "Прикладная информатика",
        "course": 3,
        "email": f"student-{uuid.uuid4()}@guu.ru",
        "password": "secret",
        "hobbies": ["sport", "cinema"],
        "onboardingAnswers": answers(),
        "consents": {
            "personalData": True,
            "terms": True,
            "aiAssessment": True,
            "policyVersion": "2026-06-01",
        },
    }
    body.update(overrides)
    return body


def test_register_login_and_me():
    email = f"student-{uuid.uuid4()}@GUU.ru"
    created = client.post("/auth/register", json=register_body(email=email))
    assert created.status_code == 201
    body = created.json()
    assert body["tokenType"] == "bearer"
    assert body["user"]["email"] == email.lower()
    assert body["user"]["role"] == "student"
    assert "password" not in body["user"]

    logged = client.post("/auth/login", json={"email": email, "password": "secret"})
    assert logged.status_code == 200
    token = logged.json()["accessToken"]
    me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["firstName"] == "Данил"


def test_missing_consent():
    body = register_body()
    body["consents"]["aiAssessment"] = False
    response = client.post("/auth/register", json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "consent_required"


def test_terms_consent_is_optional():
    body = register_body(email="terms-off@guu.ru")
    body["consents"]["terms"] = False
    response = client.post("/auth/register", json=body)
    assert response.status_code == 201


def test_duplicate_email():
    body = register_body()
    assert client.post("/auth/register", json=body).status_code == 201
    again = client.post("/auth/register", json=body)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "email_taken"


def test_invalid_login():
    response = client.post("/auth/login", json={"email": "missing@guu.ru", "password": "secret"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_refresh_rotation_and_logout():
    created = client.post("/auth/register", json=register_body())
    refresh_token = created.json()["refreshToken"]
    rotated = client.post("/auth/refresh", json={"refreshToken": refresh_token})
    assert rotated.status_code == 200
    stale = client.post("/auth/refresh", json={"refreshToken": refresh_token})
    assert stale.status_code == 401

    access = rotated.json()["accessToken"]
    fresh_refresh = rotated.json()["refreshToken"]
    headers = {"Authorization": f"Bearer {access}"}
    assert client.post("/auth/logout", json={"refreshToken": fresh_refresh}, headers=headers).status_code == 204
    denied = client.get("/me", headers=headers)
    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "token_invalid"


def test_patch_profile():
    created = client.post("/auth/register", json=register_body())
    headers = {"Authorization": f"Bearer {created.json()['accessToken']}"}
    patched = client.patch("/me", json={"course": 4, "hobbies": ["books"]}, headers=headers)
    assert patched.status_code == 200
    assert patched.json()["course"] == 4
    assert patched.json()["hobbies"] == ["books"]


def test_me_without_session():
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_invalid"
