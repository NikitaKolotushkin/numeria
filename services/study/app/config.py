from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+pysqlite:///:memory:"
    jwt_secret: str = "dev-only-change-me-not-for-production"
    service_token: str = "dev-service-token"
    ai_base_url: str = ""
    game_base_url: str = ""
    quiz_pass_score: int = 70
    ai_timeout_seconds: float = 25.0
    game_timeout_seconds: float = 2.0


settings = Settings()
