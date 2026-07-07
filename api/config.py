from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DATABASE_URL: str = "sqlite:///./healthai.db"
    SECRET_KEY: str = "changeme-super-secret-key-please-update-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    PROJECT_NAME: str = "HealthAI API"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"


settings = Settings()
