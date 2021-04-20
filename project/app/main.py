import logging
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.api.v1.routers import api_router_v1
from app.api.v2.routers import api_router_v2

API_VERSIONS_ROUTERS = {
    "v1": api_router_v1,
    "v2": api_router_v2,
}
ORIGINS = [
    "http://guarded-waters-54698.herokuapp.com",
    "https://guarded-waters-54698.herokuapp.com",
    "http://localhost",
    "https://localhost",
]


log = logging.getLogger("uvicorn")


def create_application(api_versions: List[str] = ["v2", "v1"]) -> FastAPI:
    application = FastAPI(
        title="Test-Driven Development with FastAPI and Docker",
        version="v2",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for version in api_versions:
        application.include_router(API_VERSIONS_ROUTERS[version])
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.summary"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
