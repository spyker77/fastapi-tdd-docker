import logging

from pydantic import AnyUrl
from tortoise import Tortoise, run_async

from app.config import MODELS, get_settings

log = logging.getLogger("uvicorn")


async def generate_schema(db_url: AnyUrl = get_settings().database_url) -> None:
    log.info("Initializing Tortoise...")
    await Tortoise.init(db_url=db_url, modules={"models": MODELS})
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(generate_schema())
