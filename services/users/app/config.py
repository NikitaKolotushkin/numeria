from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+pysqlite:///:memory:"
    jwt_secret: str = "dev-only-change-me-not-for-production"
    service_token: str = "dev-service-token"
    game_base_url: str = ""
    ai_base_url: str = ""
    notifications_base_url: str = ""
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    downstream_timeout_seconds: float = 2.0


settings = Settings()
