import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.balance import building_level, config_value, seed_balance
from app.clients import study_buildings, user_names
from app.errors import ApiError
from app.models import BUILDING_IDS, Building, Ledger, Player

REASONS = {"block_passed", "boss_passed", "crisis_failed", "retake_required"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_player(db: Session, user_id: uuid.UUID) -> None:
    seed_balance(db)
    if db.get(Player, user_id) is not None:
        return
    now = utcnow()
    db.add(Player(user_id=user_id, capital=0, xp=0, updated_at=now))
    for row in study_buildings(user_id):
        db.add(new_building(user_id, row, now))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def state(db: Session, user_id: uuid.UUID) -> dict:
    player = ensure_player(db, user_id)
    buildings = db.scalars(select(Building).where(Building.user_id == user_id)).all()
    ordered = sorted(buildings, key=lambda row: BUILDING_IDS.index(row.building_id))
    return {
        "capital": player.capital,
        "xp": player.xp,
        "rankPosition": rank_of(db, player),
        "totalPlayers": player_count(db),
        "buildings": [public_building(row) for row in ordered],
    }


def leaderboard(db: Session, user_id: uuid.UUID, limit: int) -> dict:
    ensure_player(db, user_id)
    if limit < 1 or limit > 50:
        raise ApiError(422, "validation_error", "Укажите limit от 1 до 50")
    rows = db.scalars(select(Player).order_by(Player.capital.desc(), Player.user_id.asc()).limit(limit)).all()
    names = user_names([row.user_id for row in rows])
    return {
        "players": [
            {
                "rankPosition": index + 1,
                "firstName": names.get(row.user_id, ""),
                "capital": row.capital,
            }
            for index, row in enumerate(rows)
        ]
    }


def apply_progress(db: Session, payload: dict) -> None:
    seed_balance(db)
    reason = payload["reason"]
    if reason not in REASONS:
        raise ApiError(422, "validation_error", "Неизвестная причина")
    source_id = payload["sourceId"]
    existing = db.scalar(select(Ledger).where(Ledger.reason == reason, Ledger.source_id == source_id))
    if existing is not None:
        return
    user_id = payload["userId"]
    player = ensure_player(db, user_id)
    capital_delta, xp_delta = deltas(db, reason)
    capital_delta = max(-player.capital, capital_delta)
    xp_delta = max(-player.xp, xp_delta)
    player.capital += capital_delta
    player.xp += xp_delta
    player.updated_at = utcnow()
    if reason != "crisis_failed":
        building = building_row(db, user_id, payload["buildingId"])
        passed_steps = max(0, min(payload["passedSteps"], payload["totalSteps"]))
        building.passed_steps = passed_steps
        building.total_steps = payload["totalSteps"]
        building.level = building_level(passed_steps, payload["totalSteps"])
        building.current_title = payload["currentTitle"]
        building.next_condition = payload["nextCondition"]
    db.add(
        Ledger(
            user_id=user_id,
            reason=reason,
            source_id=source_id,
            capital_delta=capital_delta,
            xp_delta=xp_delta,
            created_at=utcnow(),
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def deltas(db: Session, reason: str) -> tuple[int, int]:
    if reason == "block_passed":
        return config_value(db, "quiz_capital"), config_value(db, "quiz_xp")
    if reason == "boss_passed":
        return config_value(db, "boss_capital"), config_value(db, "boss_xp")
    if reason == "crisis_failed":
        return -config_value(db, "crisis_penalty"), 0
    return 0, 0


def ensure_player(db: Session, user_id: uuid.UUID) -> Player:
    player = db.get(Player, user_id)
    if player is None:
        create_player(db, user_id)
        player = db.get(Player, user_id)
    return player


def building_row(db: Session, user_id: uuid.UUID, building_id: str) -> Building:
    if building_id not in BUILDING_IDS:
        raise ApiError(422, "validation_error", "Неизвестное здание")
    row = db.get(Building, (user_id, building_id))
    if row is None:
        raise ApiError(404, "not_found", "Здание не найдено")
    return row


def new_building(user_id: uuid.UUID, row: dict, now: datetime) -> Building:
    total_steps = int(row["totalSteps"])
    passed_steps = int(row["passedSteps"])
    return Building(
        user_id=user_id,
        building_id=row["buildingId"],
        level=building_level(passed_steps, total_steps),
        passed_steps=passed_steps,
        total_steps=total_steps,
        current_title=row["currentTitle"],
        next_condition=row["nextCondition"],
    )


def public_building(row: Building) -> dict:
    return {
        "buildingId": row.building_id,
        "level": row.level,
        "passedSteps": row.passed_steps,
        "totalSteps": row.total_steps,
        "mastery": f"{row.passed_steps} / {row.total_steps}",
        "currentTitle": row.current_title,
        "nextCondition": row.next_condition,
    }


def rank_of(db: Session, player: Player) -> int:
    ahead = db.scalar(
        select(func_count()).where(
            or_(
                Player.capital > player.capital,
                (Player.capital == player.capital) & (Player.user_id < player.user_id),
            )
        )
    )
    return int(ahead or 0) + 1


def player_count(db: Session) -> int:
    return int(db.scalar(select(func_count())) or 0)


def func_count():
    from sqlalchemy import func

    return func.count(Player.user_id)
