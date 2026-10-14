import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def new_id() -> uuid.UUID:
    return uuid.uuid4()


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    building_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    disciplines: Mapped[list["Discipline"]] = relationship(back_populates="module")
    boss: Mapped["Boss"] = relationship(back_populates="module")


class Discipline(Base):
    __tablename__ = "disciplines"
    __table_args__ = (UniqueConstraint("module_id", "sort_order"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    module_id: Mapped[str] = mapped_column(String(64), ForeignKey("modules.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    module: Mapped[Module] = relationship(back_populates="disciplines")
    blocks: Mapped[list["Block"]] = relationship(back_populates="discipline")


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("discipline_id", "sort_order"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    discipline_id: Mapped[str] = mapped_column(String(64), ForeignKey("disciplines.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    discipline: Mapped[Discipline] = relationship(back_populates="blocks")


class BlockSnapshot(Base):
    __tablename__ = "block_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    block_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("blocks.id"), primary_key=True)
    theory_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        Index(
            "uq_questions_active_slot",
            "user_id",
            "block_id",
            "sort_order",
            unique=True,
            sqlite_where=text("active = 1"),
            postgresql_where=text("active"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    block_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("blocks.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    options: Mapped[list["Option"]] = relationship(back_populates="question")


class Option(Base):
    __tablename__ = "options"
    __table_args__ = (UniqueConstraint("question_id", "sort_order"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("questions.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    question: Mapped[Question] = relationship(back_populates="options")


class Boss(Base):
    __tablename__ = "bosses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    module_id: Mapped[str] = mapped_column(String(64), ForeignKey("modules.id"), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    pass_score: Mapped[int] = mapped_column(Integer, nullable=False, default=70)

    module: Mapped[Module] = relationship(back_populates="boss")


class BossSnapshot(Base):
    __tablename__ = "boss_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    boss_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bosses.id"), primary_key=True)
    prompt_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (Index("ix_quiz_attempts_user_block", "user_id", "block_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    block_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("blocks.id"), nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuizAttemptAnswer(Base):
    __tablename__ = "quiz_attempt_answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quiz_attempts.id"), primary_key=True)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("questions.id"), primary_key=True)
    option_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("options.id"), nullable=False)


class BossAttempt(Base):
    __tablename__ = "boss_attempts"
    __table_args__ = (Index("ix_boss_attempts_user_boss", "user_id", "boss_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    boss_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bosses.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer)
    verdict: Mapped[str | None] = mapped_column(String(16))
    review_text: Mapped[str | None] = mapped_column(Text)
    growth_zones: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    passed: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BlockProgress(Base):
    __tablename__ = "block_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    block_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("blocks.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    passed_attempt_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("quiz_attempts.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BossProgress(Base):
    __tablename__ = "boss_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    boss_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bosses.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    passed_attempt_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("boss_attempts.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AppliedCommand(Base):
    __tablename__ = "applied_commands"

    reason: Mapped[str] = mapped_column(String(32), primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
