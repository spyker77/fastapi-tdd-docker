import logging
import os
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings

MODELS = ["app.models.summary", "aerich.models"]

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)
    database_url: AnyUrl = os.getenv("DATABASE_URL", "sqlite://sqlite.db")
    database_test_url: AnyUrl = os.getenv("DATABASE_TEST_URL", "sqlite://test_sqlite.db")
    broker_url: AnyUrl = os.getenv("BROKER_URL", "amqp://rabbitmq")
    result_backend: AnyUrl = os.getenv("RESULT_BACKEND", "redis://redis:6379/0")


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
