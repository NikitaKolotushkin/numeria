import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog import seed_catalog
from app.clients import fetch_explanations, fetch_material, fetch_review, notify_game
from app.config import settings
from app.errors import ApiError
from app.models import (
    AppliedCommand,
    Block,
    BlockProgress,
    BlockSnapshot,
    Boss,
    BossAttempt,
    BossProgress,
    BossSnapshot,
    Discipline,
    Module,
    Option,
    Question,
    QuizAttempt,
    QuizAttemptAnswer,
)
from app.security import utcnow


def track(db: Session, user_id: uuid.UUID, building_id: str) -> dict:
    ensure_user(db, user_id)
    module = db.scalar(select(Module).where(Module.building_id == building_id))
    if module is None:
        raise ApiError(404, "not_found", "Здание не найдено")
    blocks = ordered_blocks(db, module.id)
    progress = block_progress_map(db, user_id, [block.id for block in blocks])
    boss, boss_progress = boss_pair(db, user_id, module.id)
    steps = []
    for block in blocks:
        row = progress[block.id]
        steps.append(
            {
                "kind": "block",
                "id": str(block.id),
                "title": block.title,
                "status": row.status,
                "questionCount": question_count(db, user_id, block.id),
            }
        )
    steps.append(
        {
            "kind": "boss",
            "id": str(boss.id),
            "title": boss.title,
            "status": boss_progress.status,
        }
    )
    return {
        "buildingId": building_id,
        "moduleId": module.id,
        "moduleTitle": module.title,
        "bossUnlocked": boss_progress.status in {"available", "passed"},
        "steps": steps,
    }


def open_block(db: Session, user_id: uuid.UUID, block_id: uuid.UUID) -> dict:
    ensure_user(db, user_id)
    block = db.get(Block, block_id)
    progress = db.get(BlockProgress, (user_id, block_id)) if block is not None else None
    if block is None or progress is None:
        raise ApiError(404, "not_found", "Блок не найден")
    if progress.status == "locked":
        raise ApiError(409, "step_locked", "Шаг ещё закрыт")
    snapshot = db.get(BlockSnapshot, (user_id, block_id))
    if snapshot is None:
        snapshot = create_block_snapshot(db, user_id, block)
    questions = load_questions(db, user_id, block_id)
    return {
        "id": str(block.id),
        "title": block.title,
        "theoryMarkdown": snapshot.theory_markdown,
        "questions": [public_question(question) for question in questions],
    }


def submit_block(db: Session, user_id: uuid.UUID, block_id: uuid.UUID, answers: list[dict]) -> dict:
    ensure_user(db, user_id)
    block = db.get(Block, block_id)
    progress = db.get(BlockProgress, (user_id, block_id)) if block is not None else None
    if block is None or progress is None:
        raise ApiError(404, "not_found", "Блок не найден")
    if progress.status == "locked":
        raise ApiError(409, "step_locked", "Шаг ещё закрыт")
    if progress.status == "passed":
        raise ApiError(409, "step_locked", "Шаг уже сдан")
    questions = load_questions(db, user_id, block_id)
    if not questions:
        raise ApiError(409, "step_locked", "Сначала откройте теорию")
    chosen = match_answers(questions, answers)
    correct_count = sum(1 for option in chosen.values() if option.is_correct)
    total_count = len(questions)
    score = to_score(correct_count, total_count)
    passed = score >= settings.quiz_pass_score
    attempt = QuizAttempt(
        user_id=user_id,
        block_id=block_id,
        correct_count=correct_count,
        total_count=total_count,
        score=score,
        passed=passed,
        created_at=utcnow(),
    )
    db.add(attempt)
    db.flush()
    for question_id, option in chosen.items():
        db.add(QuizAttemptAnswer(attempt_id=attempt.id, question_id=question_id, option_id=option.id))
    if passed:
        progress.status = "passed"
        progress.passed_attempt_id = attempt.id
        progress.updated_at = utcnow()
        module = module_of_block(db, block)
        refresh_availability(db, user_id, module.id)
    db.commit()
    if passed:
        notify_game(progress_body(db, user_id, module_of_block(db, block), "block_passed", attempt.id))
    snapshot = db.get(BlockSnapshot, (user_id, block_id))
    explanations = _explanations_for(snapshot.theory_markdown if snapshot else "", questions, chosen)
    return {
        "attemptId": str(attempt.id),
        "correctCount": correct_count,
        "totalCount": total_count,
        "score": score,
        "passed": passed,
        "results": [
            {
                "questionId": str(question.id),
                "correctOptionId": str(next(option.id for option in question.options if option.is_correct)),
                "explanation": explanations.get(question.id, ""),
            }
            for question in questions
        ],
    }


def _explanations_for(theory: str, questions: list[Question], chosen: dict[uuid.UUID, Option]) -> dict[uuid.UUID, str]:
    misses = []
    missed_ids = []
    for question in questions:
        picked = chosen[question.id]
        if picked.is_correct:
            continue
        correct = next(option for option in question.options if option.is_correct)
        misses.append({"prompt": question.prompt, "chosen": picked.body, "correct": correct.body})
        missed_ids.append(question.id)
    if not misses:
        return {}
    texts = fetch_explanations(theory, misses)
    result = {}
    for index, question_id in enumerate(missed_ids):
        miss = misses[index]
        fallback = f"Ответ «{miss['chosen']}» не следует из теории. Верно: «{miss['correct']}»."
        text = texts[index].strip() if texts and index < len(texts) and texts[index].strip() else fallback
        result[question_id] = text
    return result


def regenerate_block(db: Session, user_id: uuid.UUID, block_id: uuid.UUID) -> dict:
    ensure_user(db, user_id)
    block = db.get(Block, block_id)
    progress = db.get(BlockProgress, (user_id, block_id)) if block is not None else None
    if block is None or progress is None:
        raise ApiError(404, "not_found", "Блок не найден")
    if progress.status not in {"available", "retake_required"}:
        raise ApiError(409, "step_locked", "Шаг уже сдан")
    if db.get(BlockSnapshot, (user_id, block_id)) is None:
        raise ApiError(409, "step_locked", "Сначала откройте теорию")
    discipline = db.get(Discipline, block.discipline_id)
    payload = fetch_material(user_id, "block", block.title, discipline.title)
    theory, questions = parse_block_material(payload)
    snapshot = db.get(BlockSnapshot, (user_id, block_id))
    snapshot.theory_markdown = theory
    for question in load_questions(db, user_id, block_id):
        question.active = False
    db.flush()
    for index, question in enumerate(questions):
        row = Question(
            user_id=user_id,
            block_id=block.id,
            prompt=question["prompt"],
            sort_order=index,
            active=True,
        )
        db.add(row)
        db.flush()
        for option_index, option in enumerate(question["options"]):
            db.add(
                Option(
                    question_id=row.id,
                    body=option["body"],
                    is_correct=option["isCorrect"],
                    sort_order=option_index,
                )
            )
    db.commit()
    return open_block(db, user_id, block_id)


def open_boss(db: Session, user_id: uuid.UUID, boss_id: uuid.UUID) -> dict:
    ensure_user(db, user_id)
    boss = db.get(Boss, boss_id)
    progress = db.get(BossProgress, (user_id, boss_id)) if boss is not None else None
    if boss is None or progress is None:
        raise ApiError(404, "not_found", "Босс не найден")
    if progress.status == "locked":
        raise ApiError(409, "step_locked", "Шаг ещё закрыт")
    snapshot = db.get(BossSnapshot, (user_id, boss_id))
    if snapshot is None:
        snapshot = create_boss_snapshot(db, user_id, boss)
    return {"id": str(boss.id), "title": boss.title, "promptMarkdown": snapshot.prompt_markdown}


def submit_boss(db: Session, user_id: uuid.UUID, boss_id: uuid.UUID, answer_text: str) -> dict:
    ensure_user(db, user_id)
    boss = db.get(Boss, boss_id)
    progress = db.get(BossProgress, (user_id, boss_id)) if boss is not None else None
    if boss is None or progress is None:
        raise ApiError(404, "not_found", "Босс не найден")
    if progress.status != "available":
        raise ApiError(409, "step_locked", "Шаг ещё закрыт")
    if not answer_text.strip():
        raise ApiError(422, "empty_answer", "Напишите ответ")
    snapshot = db.get(BossSnapshot, (user_id, boss_id))
    if snapshot is None:
        raise ApiError(409, "step_locked", "Сначала откройте кейс")
    module = db.get(Module, boss.module_id)
    try:
        review = fetch_review(
            user_id,
            boss_id,
            snapshot.prompt_markdown,
            module_theory(db, user_id, module.id),
            answer_text.strip(),
            boss.pass_score,
        )
        score = int(review["score"])
        if score < 0 or score > 100:
            raise ValueError
        growth_zones = review["growthZones"]
        if not isinstance(growth_zones, list) or not all(isinstance(item, str) for item in growth_zones):
            raise ValueError
        review_text = str(review["reviewText"])
    except (ApiError, KeyError, TypeError, ValueError) as exc:
        if not isinstance(exc, ApiError):
            exc = ApiError(504, "ai_timeout", "Не удалось подготовить задание")
        save_boss_error(db, user_id, boss_id, answer_text.strip())
        raise exc
    passed = score >= boss.pass_score
    verdict = "accepted" if passed else "retry"
    attempt = BossAttempt(
        user_id=user_id,
        boss_id=boss_id,
        answer_text=answer_text.strip(),
        score=score,
        verdict=verdict,
        review_text=review_text,
        growth_zones=growth_zones,
        passed=passed,
        created_at=utcnow(),
    )
    db.add(attempt)
    db.flush()
    if passed:
        progress.status = "passed"
        progress.passed_attempt_id = attempt.id
        progress.updated_at = utcnow()
    db.commit()
    if passed:
        notify_game(progress_body(db, user_id, module, "boss_passed", attempt.id))
    return {
        "attemptId": str(attempt.id),
        "score": score,
        "verdict": verdict,
        "passed": passed,
        "reviewText": review_text,
        "growthZones": growth_zones,
    }


def buildings_snapshot(db: Session, user_id: uuid.UUID) -> dict:
    ensure_user(db, user_id)
    modules = db.scalars(select(Module).order_by(Module.sort_order)).all()
    buildings = []
    for module in modules:
        blocks = ordered_blocks(db, module.id)
        progress = block_progress_map(db, user_id, [block.id for block in blocks])
        boss, boss_progress = boss_pair(db, user_id, module.id)
        passed_steps = sum(1 for row in progress.values() if row.status == "passed")
        if boss_progress.status == "passed":
            passed_steps += 1
        current_title, condition = current_step(blocks, progress, boss, boss_progress)
        buildings.append(
            {
                "buildingId": module.building_id,
                "passedSteps": passed_steps,
                "totalSteps": len(blocks) + 1,
                "currentTitle": current_title,
                "nextCondition": condition,
            }
        )
    return {"buildings": buildings}


def user_progress(db: Session, user_id: uuid.UUID) -> dict:
    ensure_user(db, user_id)
    modules = db.scalars(select(Module).order_by(Module.sort_order)).all()
    buildings = []
    for module in modules:
        blocks = ordered_blocks(db, module.id)
        progress = block_progress_map(db, user_id, [block.id for block in blocks])
        _boss, boss_progress = boss_pair(db, user_id, module.id)
        passed_blocks = [row.block_id for row in progress.values() if row.status == "passed"]
        buildings.append(
            {
                "buildingId": module.building_id,
                "passedSteps": len(passed_blocks) + (1 if boss_progress.status == "passed" else 0),
                "totalSteps": len(blocks) + 1,
                "retakeBlockIds": [str(row.block_id) for row in progress.values() if row.status == "retake_required"],
            }
        )
    return {"buildings": buildings}


def apply_retake(db: Session, user_id: uuid.UUID, block_id: uuid.UUID, source_id: uuid.UUID) -> None:
    ensure_user(db, user_id)
    existing = db.get(AppliedCommand, ("retake_required", source_id))
    if existing is not None:
        return
    progress = db.get(BlockProgress, (user_id, block_id))
    if progress is None:
        raise ApiError(404, "not_found", "Блок не найден")
    progress.status = "retake_required"
    progress.passed_attempt_id = None
    progress.updated_at = utcnow()
    block = db.get(Block, block_id)
    module = module_of_block(db, block)
    _boss, boss_progress = boss_pair(db, user_id, module.id)
    if boss_progress.status != "passed":
        boss_progress.status = "locked"
        boss_progress.passed_attempt_id = None
        boss_progress.updated_at = utcnow()
    db.add(AppliedCommand(reason="retake_required", source_id=source_id))
    db.commit()
    notify_game(progress_body(db, user_id, module, "retake_required", source_id))


def admin_attempts(db: Session, user_id: uuid.UUID) -> dict:
    seed_catalog(db)
    quiz_rows = db.scalars(
        select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.created_at)
    ).all()
    boss_rows = db.scalars(
        select(BossAttempt).where(BossAttempt.user_id == user_id).order_by(BossAttempt.created_at)
    ).all()
    return {
        "quizAttempts": [quiz_attempt_view(db, row) for row in quiz_rows],
        "bossAttempts": [
            {
                "id": str(row.id),
                "bossId": str(row.boss_id),
                "answerText": row.answer_text,
                "score": row.score,
                "verdict": row.verdict,
                "reviewText": row.review_text,
                "growthZones": row.growth_zones,
                "passed": row.passed,
                "createdAt": row.created_at.isoformat(),
            }
            for row in boss_rows
        ],
    }


def ensure_user(db: Session, user_id: uuid.UUID) -> None:
    seed_catalog(db)
    existing = db.scalar(select(BlockProgress.user_id).where(BlockProgress.user_id == user_id).limit(1))
    if existing is not None:
        return
    now = utcnow()
    modules = db.scalars(select(Module)).all()
    for module in modules:
        blocks = ordered_blocks(db, module.id)
        for index, block in enumerate(blocks):
            db.add(
                BlockProgress(
                    user_id=user_id,
                    block_id=block.id,
                    status="available" if index == 0 else "locked",
                    updated_at=now,
                )
            )
        boss = db.scalar(select(Boss).where(Boss.module_id == module.id))
        db.add(BossProgress(user_id=user_id, boss_id=boss.id, status="locked", updated_at=now))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def create_block_snapshot(db: Session, user_id: uuid.UUID, block: Block) -> BlockSnapshot:
    discipline = db.get(Discipline, block.discipline_id)
    payload = fetch_material(user_id, "block", block.title, discipline.title)
    theory, questions = parse_block_material(payload)
    snapshot = BlockSnapshot(
        user_id=user_id,
        block_id=block.id,
        theory_markdown=theory,
        created_at=utcnow(),
    )
    db.add(snapshot)
    for index, question in enumerate(questions):
        row = Question(
            user_id=user_id,
            block_id=block.id,
            prompt=question["prompt"],
            sort_order=index,
            active=True,
        )
        db.add(row)
        db.flush()
        for option_index, option in enumerate(question["options"]):
            db.add(
                Option(
                    question_id=row.id,
                    body=option["body"],
                    is_correct=option["isCorrect"],
                    sort_order=option_index,
                )
            )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        snapshot = db.get(BlockSnapshot, (user_id, block.id))
        if snapshot is None:
            raise
        return snapshot
    return snapshot


def create_boss_snapshot(db: Session, user_id: uuid.UUID, boss: Boss) -> BossSnapshot:
    module = db.get(Module, boss.module_id)
    payload = fetch_material(user_id, "boss", boss.title, module.title)
    prompt = payload.get("promptMarkdown") if isinstance(payload, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    snapshot = BossSnapshot(
        user_id=user_id,
        boss_id=boss.id,
        prompt_markdown=prompt,
        created_at=utcnow(),
    )
    db.add(snapshot)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        snapshot = db.get(BossSnapshot, (user_id, boss.id))
        if snapshot is None:
            raise
    return snapshot


def parse_block_material(payload: dict) -> tuple[str, list[dict]]:
    if not isinstance(payload, dict):
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    theory = payload.get("theoryMarkdown")
    questions = payload.get("questions")
    if not isinstance(theory, str) or not theory.strip() or not isinstance(questions, list) or not questions:
        raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
    parsed = []
    for question in questions:
        prompt = question.get("prompt") if isinstance(question, dict) else None
        options = question.get("options") if isinstance(question, dict) else None
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(options, list) or len(options) != 4:
            raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
        correct = 0
        parsed_options = []
        for option in options:
            if not isinstance(option, dict) or not isinstance(option.get("body"), str) or not option["body"].strip():
                raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
            if option.get("isCorrect") is True:
                correct += 1
            parsed_options.append({"body": option["body"].strip(), "isCorrect": option.get("isCorrect") is True})
        if correct != 1:
            raise ApiError(504, "ai_timeout", "Не удалось подготовить задание")
        parsed.append({"prompt": prompt.strip(), "options": parsed_options})
    return theory.strip(), parsed


def match_answers(questions: list[Question], answers: list[dict]) -> dict[uuid.UUID, Option]:
    expected = {question.id: question for question in questions}
    if len(answers) != len(expected):
        raise ApiError(422, "answers_incomplete", "Ответьте на все вопросы")
    chosen: dict[uuid.UUID, Option] = {}
    for answer in answers:
        question_id = answer["questionId"]
        option_id = answer["optionId"]
        question = expected.get(question_id)
        if question is None or question_id in chosen:
            raise ApiError(422, "answers_incomplete", "Ответьте на все вопросы")
        option = next((item for item in question.options if item.id == option_id), None)
        if option is None:
            raise ApiError(422, "answers_incomplete", "Ответьте на все вопросы")
        chosen[question_id] = option
    if set(chosen) != set(expected):
        raise ApiError(422, "answers_incomplete", "Ответьте на все вопросы")
    return chosen


def refresh_availability(db: Session, user_id: uuid.UUID, module_id: str) -> None:
    blocks = ordered_blocks(db, module_id)
    progress = block_progress_map(db, user_id, [block.id for block in blocks])
    _boss, boss_progress = boss_pair(db, user_id, module_id)
    if any(row.status == "retake_required" for row in progress.values()):
        if boss_progress.status != "passed":
            boss_progress.status = "locked"
            boss_progress.updated_at = utcnow()
        return
    all_passed = True
    opened = False
    for block in blocks:
        row = progress[block.id]
        if row.status == "passed":
            continue
        all_passed = False
        if not opened:
            if row.status == "locked":
                row.status = "available"
                row.updated_at = utcnow()
            opened = True
    if all_passed and boss_progress.status == "locked":
        boss_progress.status = "available"
        boss_progress.updated_at = utcnow()


def progress_body(db: Session, user_id: uuid.UUID, module: Module, reason: str, source_id: uuid.UUID) -> dict:
    blocks = ordered_blocks(db, module.id)
    progress = block_progress_map(db, user_id, [block.id for block in blocks])
    _boss, boss_progress = boss_pair(db, user_id, module.id)
    passed_steps = sum(1 for row in progress.values() if row.status == "passed")
    if boss_progress.status == "passed":
        passed_steps += 1
    current_title, condition = current_step(blocks, progress, _boss, boss_progress)
    return {
        "userId": str(user_id),
        "reason": reason,
        "sourceId": str(source_id),
        "buildingId": module.building_id,
        "passedSteps": passed_steps,
        "totalSteps": len(blocks) + 1,
        "currentTitle": current_title,
        "nextCondition": condition,
    }


def current_step(blocks, progress, boss, boss_progress) -> tuple[str, str]:
    for block in blocks:
        row = progress[block.id]
        if row.status == "retake_required":
            return block.title, f"Пересдать блок {block.title}"
    for block in blocks:
        row = progress[block.id]
        if row.status != "passed":
            return block.title, "Пройти теорию и тест"
    if boss_progress.status != "passed":
        return boss.title, "Сдать все блоки модуля"
    return boss.title, "Модуль сдан"


def ordered_blocks(db: Session, module_id: str) -> list[Block]:
    disciplines = db.scalars(
        select(Discipline).where(Discipline.module_id == module_id).order_by(Discipline.sort_order)
    ).all()
    blocks: list[Block] = []
    for discipline in disciplines:
        blocks.extend(
            db.scalars(select(Block).where(Block.discipline_id == discipline.id).order_by(Block.sort_order)).all()
        )
    return blocks


def block_progress_map(db: Session, user_id: uuid.UUID, block_ids: list[uuid.UUID]) -> dict:
    rows = db.scalars(
        select(BlockProgress).where(BlockProgress.user_id == user_id, BlockProgress.block_id.in_(block_ids))
    ).all()
    return {row.block_id: row for row in rows}


def boss_pair(db: Session, user_id: uuid.UUID, module_id: str) -> tuple[Boss, BossProgress]:
    boss = db.scalar(select(Boss).where(Boss.module_id == module_id))
    progress = db.get(BossProgress, (user_id, boss.id))
    return boss, progress


def module_of_block(db: Session, block: Block) -> Module:
    discipline = db.get(Discipline, block.discipline_id)
    return db.get(Module, discipline.module_id)


def question_count(db: Session, user_id: uuid.UUID, block_id: uuid.UUID) -> int:
    rows = db.scalars(select(Question.id).where(Question.user_id == user_id, Question.block_id == block_id)).all()
    return len(rows)


def load_questions(db: Session, user_id: uuid.UUID, block_id: uuid.UUID) -> list[Question]:
    questions = db.scalars(
        select(Question)
        .where(Question.user_id == user_id, Question.block_id == block_id, Question.active.is_(True))
        .order_by(Question.sort_order)
    ).all()
    for question in questions:
        question.options.sort(key=lambda option: option.sort_order)
    return list(questions)


def public_question(question: Question) -> dict:
    return {
        "id": str(question.id),
        "prompt": question.prompt,
        "options": [{"id": str(option.id), "body": option.body} for option in question.options],
    }


def module_theory(db: Session, user_id: uuid.UUID, module_id: str) -> str:
    parts = []
    for block in ordered_blocks(db, module_id):
        snapshot = db.get(BlockSnapshot, (user_id, block.id))
        if snapshot is not None:
            parts.append(snapshot.theory_markdown)
    return "\n\n".join(parts)


def save_boss_error(db: Session, user_id: uuid.UUID, boss_id: uuid.UUID, answer_text: str) -> None:
    db.add(
        BossAttempt(
            user_id=user_id,
            boss_id=boss_id,
            answer_text=answer_text,
            verdict="error",
            growth_zones=[],
            passed=False,
            created_at=utcnow(),
        )
    )
    db.commit()


def quiz_attempt_view(db: Session, attempt: QuizAttempt) -> dict:
    links = db.scalars(select(QuizAttemptAnswer).where(QuizAttemptAnswer.attempt_id == attempt.id)).all()
    answers = []
    for link in links:
        question = db.get(Question, link.question_id)
        option = db.get(Option, link.option_id)
        answers.append(
            {
                "questionId": str(link.question_id),
                "prompt": question.prompt,
                "optionId": str(link.option_id),
                "body": option.body,
                "isCorrect": option.is_correct,
            }
        )
    return {
        "id": str(attempt.id),
        "blockId": str(attempt.block_id),
        "score": attempt.score,
        "passed": attempt.passed,
        "createdAt": attempt.created_at.isoformat(),
        "answers": answers,
    }


def to_score(correct_count: int, total_count: int) -> int:
    value = (Decimal(correct_count) / Decimal(total_count) * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(value)
