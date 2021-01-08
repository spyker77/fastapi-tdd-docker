import logging
import os
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings

from .db import DB_URL

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = bool(os.getenv("TESTING", 0))
    database_url: AnyUrl = DB_URL


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
