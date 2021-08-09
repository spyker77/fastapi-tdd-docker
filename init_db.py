import logging

from tortoise import Tortoise, run_async

from app.config import get_settings

settings = get_settings()

log = logging.getLogger("uvicorn")


async def generate_schema(db_url: str = settings.DATABASE_URL) -> None:
    log.info("Initializing Tortoise...")
    await Tortoise.init(db_url=db_url, modules={"models": settings.MODELS})
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(generate_schema())
