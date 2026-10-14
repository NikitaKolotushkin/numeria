import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def new_id() -> uuid.UUID:
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    university: Mapped[str] = mapped_column(String(160), nullable=False)
    direction: Mapped[str] = mapped_column(String(160), nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    consents: Mapped["Consent"] = relationship(back_populates="user")
    hobbies: Mapped[list["Hobby"]] = relationship(back_populates="user")
    onboarding_answers: Mapped[list["OnboardingAnswer"]] = relationship(back_populates="user")


class Consent(Base):
    __tablename__ = "consents"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), primary_key=True)
    personal_data_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    terms_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ai_assessment_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(32), nullable=False)

    user: Mapped[User] = relationship(back_populates="consents")


class Hobby(Base):
    __tablename__ = "hobbies"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), primary_key=True)
    hobby_id: Mapped[str] = mapped_column(String(32), primary_key=True)

    user: Mapped[User] = relationship(back_populates="hobbies")


class OnboardingAnswer(Base):
    __tablename__ = "onboarding_answers"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_index: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped[User] = relationship(back_populates="onboarding_answers")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AccessDenylist(Base):
    __tablename__ = "access_denylist"
    __table_args__ = (UniqueConstraint("jti"),)

    jti: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
