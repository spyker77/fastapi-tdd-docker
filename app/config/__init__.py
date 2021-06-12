import logging
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings

log = logging.getLogger("uvicorn")


class DockerSettings(BaseSettings):
    ENVIRONMENT: str = "dev"
    TESTING: bool = False
    DATABASE_URL: AnyUrl = "sqlite://sqlite.db"
    DATABASE_TEST_URL: AnyUrl = "sqlite://test_sqlite.db"
    BROKER_URL: AnyUrl = "amqp://rabbitmq"
    RESULT_BACKEND: AnyUrl = "redis://redis:6379/0"


class AppSettings(BaseSettings):
    ORIGINS: List[AnyHttpUrl] = [
        "http://guarded-waters-54698.herokuapp.com",
        "https://guarded-waters-54698.herokuapp.com",
        "http://localhost",
        "https://localhost",
    ]
    MODELS: List[str] = ["app.models.summary", "aerich.models"]


class Settings(DockerSettings, AppSettings):
    pass


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
