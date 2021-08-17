import logging
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, Field

log = logging.getLogger("uvicorn")


class DockerSettings(BaseSettings):
    ENVIRONMENT: str = "dev"
    TESTING: bool = False
    # To generate a new SECRET_KEY, run this command:
    # openssl rand -hex 32
    SECRET_KEY: str
    DATABASE_URL: str = Field("postgres://postgres@db/postgres")
    DATABASE_TEST_URL: str = Field("sqlite://:memory:")
    BROKER_URL: AnyUrl = Field("amqp://rabbitmq")
    RESULT_BACKEND: AnyUrl = Field("redis://redis")


class AppSettings(BaseSettings):
    AUTH_TOKEN_URL: str = "/api/token"
    MODELS: List[str] = Field(["app.models", "aerich.models"])
    ORIGINS: List[AnyHttpUrl] = Field(
        [
            "http://fastapi-tdd-docker-spyker77.herokuapp.com",
            "https://fastapi-tdd-docker-spyker77.herokuapp.com",
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
