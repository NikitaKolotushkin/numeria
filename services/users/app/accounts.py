import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ApiError
from app.models import AccessDenylist, Consent, Hobby, OnboardingAnswer, RefreshToken, User
from app.schemas import AuthOut, PatchIn, RegisterIn, UserOut
from app.security import (
    decode_access,
    encode_access,
    hash_password,
    hash_refresh,
    new_refresh_token,
    utcnow,
    verify_password,
)
from app.config import settings
from app.validation import require_course, require_email, require_hobbies, require_text


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        university=user.university,
        direction=user.direction,
        course=user.course,
        hobbies=[hobby.hobby_id for hobby in user.hobbies],
        role=user.role,
    )


def issue_session(db: Session, user: User) -> AuthOut:
    jti = uuid.uuid4()
    access = encode_access(user.id, user.role, jti)
    refresh = new_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh(refresh),
            expires_at=utcnow() + timedelta(days=settings.refresh_token_days),
            created_at=utcnow(),
        )
    )
    db.commit()
    db.refresh(user)
    return AuthOut(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        user=user_out(user),
    )


def register_user(db: Session, payload: RegisterIn) -> tuple[User, AuthOut]:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise ApiError(409, "email_taken", "Почта уже зарегистрирована")

    now = utcnow()
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        university=payload.university,
        direction=payload.direction,
        course=payload.course,
        role="student",
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    db.add(
        Consent(
            user_id=user.id,
            personal_data_at=now,
            terms_at=now,
            ai_assessment_at=now,
            policy_version=payload.consents.policy_version,
        )
    )
    for hobby_id in payload.hobbies:
        db.add(Hobby(user_id=user.id, hobby_id=hobby_id))
    for answer in payload.onboarding_answers:
        db.add(
            OnboardingAnswer(
                user_id=user.id,
                question_id=answer.question_id,
                option_index=answer.option_index,
            )
        )
    db.commit()
    db.refresh(user)
    return user, issue_session(db, user)


def login_user(db: Session, email: str, password: str) -> AuthOut:
    try:
        normalized = require_email(email)
    except ApiError:
        raise ApiError(401, "invalid_credentials", "Почта или пароль неверны")
    user = db.scalar(select(User).where(User.email == normalized))
    if user is None or not verify_password(password, user.password_hash):
        raise ApiError(401, "invalid_credentials", "Почта или пароль неверны")
    return issue_session(db, user)


def aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def rotate_refresh(db: Session, refresh_token: str) -> AuthOut:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh(refresh_token)))
    now = utcnow()
    if row is None or row.revoked_at is not None or aware(row.expires_at) <= now:
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    row.revoked_at = now
    user = db.get(User, row.user_id)
    if user is None:
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    return issue_session(db, user)


def logout_user(db: Session, user: User, jti: uuid.UUID, access_expires, refresh_token: str) -> None:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh(refresh_token)))
    now = utcnow()
    if row is None or row.user_id != user.id or row.revoked_at is not None or aware(row.expires_at) <= now:
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    row.revoked_at = now
    if db.get(AccessDenylist, jti) is None:
        db.add(AccessDenylist(jti=jti, expires_at=access_expires))
    db.commit()


def patch_user(db: Session, user: User, payload: PatchIn) -> UserOut:
    fields = payload.model_fields_set
    if "first_name" in fields:
        user.first_name = require_text(payload.first_name or "", 80, "Укажите имя")
    if "last_name" in fields:
        user.last_name = require_text(payload.last_name or "", 80, "Укажите фамилию")
    if "university" in fields:
        user.university = require_text(payload.university or "", 160, "Укажите ваш университет")
    if "direction" in fields:
        user.direction = require_text(payload.direction or "", 160, "Укажите направление обучения")
    if "course" in fields:
        user.course = require_course(payload.course if payload.course is not None else 0)
    if "hobbies" in fields:
        hobbies = require_hobbies(payload.hobbies or [])
        for hobby in list(user.hobbies):
            db.delete(hobby)
        db.flush()
        for hobby_id in hobbies:
            db.add(Hobby(user_id=user.id, hobby_id=hobby_id))
    user.updated_at = utcnow()
    db.commit()
    db.refresh(user)
    return user_out(user)


def read_access(db: Session, token: str) -> tuple[User, uuid.UUID, datetime]:
    try:
        payload = decode_access(token)
        user_id = uuid.UUID(payload["sub"])
        jti = uuid.UUID(payload["jti"])
        expires = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    if db.get(AccessDenylist, jti) is not None:
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    user = db.get(User, user_id)
    if user is None:
        raise ApiError(401, "token_invalid", "Сессия недействительна")
    return user, jti, expires
