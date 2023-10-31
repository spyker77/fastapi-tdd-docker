import logging
from contextlib import asynccontextmanager
from typing import AsyncContextManager, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import home_page, token
from app.api.v2.routers import api_router_v2
from app.config import get_settings
from app.database import async_engine

settings = get_settings()

log = logging.getLogger("uvicorn")

API_VERSIONS_ROUTERS = {"v2": api_router_v2}


def create_application(api_versions: List[str] = ["v2"], lifespan: AsyncContextManager = None) -> FastAPI:
    application = FastAPI(
        title="Test-Driven Development with FastAPI and Docker",
        description="""Create a random user and then authorize to play around with options.
        Authorized users can create and read everything, but update and delete only their own entries.
        """,
        version="v2",
        lifespan=lifespan,
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up...")
    async with async_engine.begin():
        pass

    yield

    log.info("Shutting down...")
    await async_engine.dispose()


app = create_application(lifespan=lifespan)
