from app.errors import ApiError
from app.schemas import OnboardingAnswerIn, RegisterIn
from app.security import HOBBY_IDS, ONBOARDING_QUESTIONS


def normalize_email(email: str) -> str:
    return email.strip().lower()


def require_text(value: str, limit: int, message: str) -> str:
    cleaned = value.strip()
    if not cleaned or len(cleaned) > limit:
        raise ApiError(422, "validation_error", message)
    return cleaned


def require_course(course: int) -> int:
    if course < 1 or course > 6:
        raise ApiError(422, "validation_error", "Укажите курс цифрой от 1 до 6")
    return course


def require_password(password: str) -> str:
    if len(password) < 4 or len(password) > 128:
        raise ApiError(422, "validation_error", "Пароль должен содержать от 4 до 128 символов")
    return password


def require_email(email: str) -> str:
    normalized = normalize_email(email)
    if len(normalized) > 254 or " " in normalized:
        raise ApiError(422, "validation_error", "Введите корректный email")
    local, separator, domain = normalized.partition("@")
    if not separator or not local or not domain or "@" in domain:
        raise ApiError(422, "validation_error", "Введите корректный email")
    return normalized


def require_hobbies(hobbies: list[str]) -> list[str]:
    if not hobbies or len(hobbies) > 6 or len(set(hobbies)) != len(hobbies):
        raise ApiError(422, "validation_error", "Выберите от одного до шести разных интересов")
    if any(hobby not in HOBBY_IDS for hobby in hobbies):
        raise ApiError(422, "validation_error", "Выберите интерес из списка")
    return hobbies


def require_onboarding(answers: list[OnboardingAnswerIn]) -> list[OnboardingAnswerIn]:
    seen = [answer.question_id for answer in answers]
    if set(seen) != ONBOARDING_QUESTIONS or len(seen) != len(ONBOARDING_QUESTIONS):
        raise ApiError(422, "validation_error", "Ответьте на все вопросы теста")
    if any(answer.option_index < 0 or answer.option_index > 3 for answer in answers):
        raise ApiError(422, "validation_error", "Ответьте на все вопросы теста")
    return answers


def require_policy_version(version: str) -> str:
    cleaned = version.strip()
    if not cleaned or len(cleaned) > 32:
        raise ApiError(422, "validation_error", "Укажите версию политики")
    return cleaned


def validate_register(payload: RegisterIn) -> RegisterIn:
    if not (payload.consents.personal_data and payload.consents.terms and payload.consents.ai_assessment):
        raise ApiError(422, "consent_required", "Нужны три согласия")
    payload.first_name = require_text(payload.first_name, 80, "Укажите имя")
    payload.last_name = require_text(payload.last_name, 80, "Укажите фамилию")
    payload.university = require_text(payload.university, 160, "Укажите ваш университет")
    payload.direction = require_text(payload.direction, 160, "Укажите направление обучения")
    payload.course = require_course(payload.course)
    payload.password = require_password(payload.password)
    payload.email = require_email(payload.email)
    payload.hobbies = require_hobbies(payload.hobbies)
    payload.onboarding_answers = require_onboarding(payload.onboarding_answers)
    payload.consents.policy_version = require_policy_version(payload.consents.policy_version)
    return payload
