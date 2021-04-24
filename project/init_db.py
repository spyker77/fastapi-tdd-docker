import logging
import os

from tortoise import Tortoise, run_async

from app.main import MODELS

log = logging.getLogger("uvicorn")


async def generate_schema(db_url=os.environ.get("DATABASE_URL")) -> None:
    log.info("Initializing Tortoise...")
    await Tortoise.init(
        db_url=db_url,
        modules={"models": MODELS},
    )
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(generate_schema())
