import logging
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, Field

log = logging.getLogger("uvicorn")


class DockerSettings(BaseSettings):
    ENVIRONMENT: str = "dev"
    TESTING: bool = False
    DATABASE_URL: AnyUrl = Field("sqlite://sqlite.db")
    DATABASE_TEST_URL: AnyUrl = Field("sqlite://test_sqlite.db")
    BROKER_URL: AnyUrl = Field("amqp://rabbitmq")
    RESULT_BACKEND: AnyUrl = Field("redis://redis:6379/0")


class AppSettings(BaseSettings):
    MODELS: List[str] = Field(["app.models.summary", "aerich.models"])
    ORIGINS: List[AnyHttpUrl] = Field(
        [
            "http://guarded-waters-54698.herokuapp.com",
            "https://guarded-waters-54698.herokuapp.com",
            "http://localhost",
            "https://localhost",
        ]
    )


class Settings(DockerSettings, AppSettings):
    pass


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
