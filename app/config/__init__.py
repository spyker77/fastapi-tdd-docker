import logging
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    ENVIRONMENT: str
    TESTING: bool
    # To generate a new SECRET_KEY, run this command: openssl rand -hex 32
    SECRET_KEY: str
    DATABASE_URL: str
    DATABASE_TEST_URL: str
    BROKER_URL: str
    RESULT_BACKEND: str
    SUMMARIZER_MODEL_RU: str
    SUMMARIZER_MODEL_EN: str
    LANGUAGE_DETECTION_MODEL: str

    AUTH_TOKEN_URL: str = "/api/token"
    ORIGINS: List[str] = Field(["http://localhost", "https://localhost"])

    class Config:
        env_prefix = ""
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
