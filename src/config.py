import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "sk-mock-key-for-local-testing"
    OPENAI_MODEL: str = "gpt-4o"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    RESPONSE_TIMEOUT_SECONDS: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
