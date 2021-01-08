import logging
import os
import re
from urllib.parse import urlparse

from fastapi import FastAPI
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

PARSED_DB_URL = urlparse(os.environ.get("DATABASE_URL"))
DB_CREDENTIALS = re.split(":|@", str(PARSED_DB_URL.netloc)) + [
    str(PARSED_DB_URL.path).lstrip("/")
]


# Helper for migrations: https://github.com/testdrivenio/fastapi-tortoise-aerich
TORTOISE_ORM = {
    "connections": {
        "default": os.environ.get("DATABASE_URL")
        if "sqlite" in PARSED_DB_URL
        else {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "user": DB_CREDENTIALS[0],
                "password": DB_CREDENTIALS[1],
                "host": DB_CREDENTIALS[2],
                "port": DB_CREDENTIALS[3],
                "database": DB_CREDENTIALS[4],
                "ssl": "require" if os.environ.get("ENVIRONMENT") == "prod" else False,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}


log = logging.getLogger("uvicorn")


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config={
            "connections": {
                "default": os.environ.get("DATABASE_URL")
                if "sqlite" in PARSED_DB_URL
                else {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "user": DB_CREDENTIALS[0],
                        "password": DB_CREDENTIALS[1],
                        "host": DB_CREDENTIALS[2],
                        "port": DB_CREDENTIALS[3],
                        "database": DB_CREDENTIALS[4],
                        "ssl": "require"
                        if os.environ.get("ENVIRONMENT") == "prod"
                        else False,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": ["app.models.tortoise"],
                    "default_connection": "default",
                },
            },
        },
        generate_schemas=False,
        add_exception_handlers=True,
    )


async def generate_schema() -> None:
    log.info("Initializing Tortoise...")
    await Tortoise.init(
        config={
            "connections": {
                "default": os.environ.get("DATABASE_URL")
                if "sqlite" in PARSED_DB_URL
                else {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "user": DB_CREDENTIALS[0],
                        "password": DB_CREDENTIALS[1],
                        "host": DB_CREDENTIALS[2],
                        "port": DB_CREDENTIALS[3],
                        "database": DB_CREDENTIALS[4],
                        "ssl": "require"
                        if os.environ.get("ENVIRONMENT") == "prod"
                        else False,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": ["models.tortoise"],
                    "default_connection": "default",
                },
            },
        }
    )
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(generate_schema())
