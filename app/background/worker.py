from celery import Celery

from app.config import get_settings

settings = get_settings()
celery = Celery(
    main=__name__,
    backend=settings.celery_result_backend,
    broker=settings.celery_broker_url,
    include=["app.background.tasks"],
)
