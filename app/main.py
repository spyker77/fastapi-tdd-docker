import logging
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.api import home_page, token
from app.api.v2.routers import api_router_v2
from app.config import get_settings

settings = get_settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": settings.MODELS,
            "default_connection": "default",
        },
    },
}

API_VERSIONS_ROUTERS = {"v2": api_router_v2}

log = logging.getLogger("uvicorn")


def create_application(api_versions: List[str] = ["v2"]) -> FastAPI:
    application = FastAPI(
        title="Test-Driven Development with FastAPI and Docker",
        description="""Create a random user and then authorize to play around with options.
        Authorized users can create and read everything, but update and delete only their own entries.
        """,
        version="v2",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(home_page.router)
    application.include_router(token.router)
    for version in api_versions:
        application.include_router(API_VERSIONS_ROUTERS[version])
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": settings.MODELS},
        generate_schemas=False,
        add_exception_handlers=True,
    )


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
