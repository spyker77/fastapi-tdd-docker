import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ping, summaries
from app.db import init_db

ORIGINS = [
    "http://guarded-waters-54698.herokuapp.com",
    "https://guarded-waters-54698.herokuapp.com",
    "http://localhost",
    "https://localhost",
]


log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(ping.router)
    application.include_router(
        summaries.router, prefix="/summaries", tags=["summaries"]
    )
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
