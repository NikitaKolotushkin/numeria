CORRECT_OPTIONS = {1: 2, 2: 1, 3: 1, 4: 2, 5: 1}

TITLES = {
    0: "Начинающий",
    1: "Начинающий",
    2: "Знакомый с основами",
    3: "Разбирается",
    4: "Уверенный",
    5: "Подготовленный",
}


def readiness_title(answers: list[dict] | None) -> str:
    if not answers:
        return ""
    score = 0
    for item in answers:
        if not isinstance(item, dict):
            continue
        question_id = item.get("questionId")
        if question_id in CORRECT_OPTIONS and item.get("optionIndex") == CORRECT_OPTIONS[question_id]:
            score += 1
    return TITLES[min(score, 5)]
