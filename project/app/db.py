import logging
import os
import re
from urllib.parse import urlparse

from fastapi import FastAPI
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

# Special case of parsing the database url tested on SQLite and PostgreSQL.
# It's done to enable sslmode and prevent database connection error in production.
db_url = os.environ.get("DATABASE_URL")
if (db_url is not None) and ("sqlite" in db_url):
    DB_CONNECTION = {"default": db_url}
elif db_url is not None:
    parsed_db_url = urlparse(db_url)
    db_credentials = re.split(":|@", str(parsed_db_url.netloc)) + [
        str(parsed_db_url.path).lstrip("/")
    ]
    DB_CONNECTION = {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "user": db_credentials[0],
                "password": db_credentials[1],
                "host": db_credentials[2],
                "port": db_credentials[3],
                "database": db_credentials[4],
                "ssl": "require" if os.environ.get("ENVIRONMENT") == "prod" else False,
            },
        }
    }


# Helper for migrations: https://github.com/testdrivenio/fastapi-tortoise-aerich
TORTOISE_ORM = {
    "connections": DB_CONNECTION,
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
            "connections": DB_CONNECTION,
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
            "connections": DB_CONNECTION,
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
