import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

BUILDING_IDS = ("office", "factory", "laboratory", "marketing", "accounting")


def new_id() -> uuid.UUID:
    return uuid.uuid4()


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (Index("ix_players_rank", "capital", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    capital: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    readiness: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Building(Base):
    __tablename__ = "buildings"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("players.user_id"), primary_key=True)
    building_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    passed_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    current_title: Mapped[str] = mapped_column(String(200), nullable=False)
    next_condition: Mapped[str] = mapped_column(String(200), nullable=False)


class Ledger(Base):
    __tablename__ = "ledger"
    __table_args__ = (UniqueConstraint("reason", "source_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("players.user_id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    capital_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BalanceConfig(Base):
    __tablename__ = "balance_config"

    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
