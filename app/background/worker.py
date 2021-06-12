from celery import Celery

from app.config import get_settings

settings = get_settings()

celery = Celery(
    main=__name__,
    backend=settings.RESULT_BACKEND,
    broker=settings.BROKER_URL,
    include=["app.background.tasks"],
)
