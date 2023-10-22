import logging
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, Field

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    ENVIRONMENT: str
    TESTING: bool
    # To generate a new SECRET_KEY, run this command: openssl rand -hex 32
    SECRET_KEY: str
    DATABASE_URL: str
    DATABASE_TEST_URL: str
    BROKER_URL: AnyUrl
    RESULT_BACKEND: AnyUrl
    SUMMARIZER_MODEL: str

    AUTH_TOKEN_URL: str = "/api/token"
    ORIGINS: List[AnyHttpUrl] = Field(["http://localhost", "https://localhost"])

    class Config:
        env_prefix = ""
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
