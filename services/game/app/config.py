from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+pysqlite:///:memory:"
    jwt_secret: str = "dev-only-change-me-not-for-production"
    service_token: str = "dev-service-token"
    study_base_url: str = ""
    users_base_url: str = ""
    downstream_timeout_seconds: float = 2.0


settings = Settings()
