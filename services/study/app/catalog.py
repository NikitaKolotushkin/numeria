import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Block, Boss, Discipline, Module

NAMESPACE = uuid.UUID("6f0c1e2a-7b34-4d5e-9a10-112233445566")

MODULES = (
    ("foundations", "office", "Основы и введение", 0),
    ("production", "factory", "Производство", 1),
    ("analytics", "laboratory", "Аналитика и статистика", 2),
    ("foreign", "marketing", "Международные связи", 3),
    ("books", "accounting", "Бухгалтерский учет", 4),
)

DISCIPLINES = (
    ("intro_theory", "foundations", "Введение в экономическую теорию", 0),
    ("management", "foundations", "Менеджмент", 1),
    ("macro", "foundations", "Макроэкономика", 2),
    ("enterprise", "production", "Экономика предприятия", 0),
    ("micro", "production", "Микроэкономика", 1),
    ("math_stat", "analytics", "Математическая статистика", 0),
    ("econometrics", "analytics", "Эконометрика", 1),
    ("marketing", "foreign", "Маркетинг", 0),
    ("international", "foreign", "Международная экономика", 1),
    ("accounting", "books", "Бухгалтерский учет", 0),
)


def slot_id(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{kind}:{key}")


def seed_catalog(db: Session) -> None:
    ready = db.scalar(select(func.count()).select_from(Block))
    if ready == 30:
        return
    for module_id, building_id, title, sort_order in MODULES:
        db.add(Module(id=module_id, building_id=building_id, title=title, sort_order=sort_order))
    for discipline_id, module_id, title, sort_order in DISCIPLINES:
        db.add(Discipline(id=discipline_id, module_id=module_id, title=title, sort_order=sort_order))
        for block_order in range(3):
            db.add(
                Block(
                    id=slot_id("block", f"{discipline_id}:{block_order}"),
                    discipline_id=discipline_id,
                    title=f"{title}, блок {block_order + 1}",
                    sort_order=block_order,
                )
            )
    for module_id, _building_id, _title, _sort_order in MODULES:
        db.add(
            Boss(
                id=slot_id("boss", module_id),
                module_id=module_id,
                title="Битва с боссом",
                pass_score=70,
            )
        )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
