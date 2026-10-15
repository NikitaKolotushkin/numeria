from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BalanceConfig

DEFAULTS = {
    "quiz_capital": 100,
    "quiz_xp": 10,
    "boss_capital": 400,
    "boss_xp": 30,
    "crisis_penalty": 50,
}

FALLBACK_BUILDINGS = (
    ("office", 6, "Введение в экономическую теорию, блок 1"),
    ("factory", 6, "Экономика предприятия, блок 1"),
    ("laboratory", 6, "Математическая статистика, блок 1"),
    ("marketing", 6, "Маркетинг, блок 1"),
    ("accounting", 6, "Бухгалтерский учет, блок 1"),
)


def seed_balance(db: Session) -> None:
    ready = db.scalar(select(func.count()).select_from(BalanceConfig))
    if ready == len(DEFAULTS):
        return
    for key, value in DEFAULTS.items():
        if db.get(BalanceConfig, key) is None:
            db.add(BalanceConfig(key=key, value=value))
    db.commit()


def config_value(db: Session, key: str) -> int:
    seed_balance(db)
    row = db.get(BalanceConfig, key)
    return row.value if row is not None else DEFAULTS[key]


def building_level(passed_steps: int, total_steps: int) -> int:
    passed = max(0, min(passed_steps, total_steps))
    if total_steps <= 0:
        return 1
    return min(5, 1 + (4 * passed) // total_steps)
