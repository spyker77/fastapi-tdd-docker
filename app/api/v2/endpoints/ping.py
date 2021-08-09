from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/", name="pong")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.ENVIRONMENT,
        "testing": settings.TESTING,
    }
