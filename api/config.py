from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://healthai:changeme@postgres:5432/healthai_coach"
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    PROJECT_NAME: str = "HealthAI API"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"


settings = Settings()
