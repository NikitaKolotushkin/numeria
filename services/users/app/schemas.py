import uuid

from pydantic import BaseModel, ConfigDict, Field


class ConsentIn(BaseModel):
    personal_data: bool = Field(alias="personalData")
    terms: bool
    ai_assessment: bool = Field(alias="aiAssessment")
    policy_version: str = Field(alias="policyVersion")

    model_config = ConfigDict(populate_by_name=True)


class OnboardingAnswerIn(BaseModel):
    question_id: int = Field(alias="questionId")
    option_index: int = Field(alias="optionIndex")

    model_config = ConfigDict(populate_by_name=True)


class RegisterIn(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    university: str
    direction: str
    course: int
    email: str
    password: str
    hobbies: list[str]
    onboarding_answers: list[OnboardingAnswerIn] = Field(alias="onboardingAnswers")
    consents: ConsentIn

    model_config = ConfigDict(populate_by_name=True)


class LoginIn(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str = Field(alias="refreshToken")

    model_config = ConfigDict(populate_by_name=True)


class PatchIn(BaseModel):
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    university: str | None = None
    direction: str | None = None
    course: int | None = None
    hobbies: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    university: str
    direction: str
    course: int
    hobbies: list[str]
    role: str

    model_config = ConfigDict(populate_by_name=True)


class AuthOut(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    refresh_token: str = Field(serialization_alias="refreshToken")
    token_type: str = Field(serialization_alias="tokenType")
    user: UserOut

    model_config = ConfigDict(populate_by_name=True)
