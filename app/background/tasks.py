from typing import Optional
from uuid import UUID

import nltk
from newspaper import Article, Config
from pydantic import AnyHttpUrl
from tortoise import Tortoise, run_async

from app.config import get_settings
from app.models import Summary

from .worker import celery

CUSTOM_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0"

config = Config()

config.browser_user_agent = CUSTOM_USER_AGENT

settings = get_settings()


async def _update_summary(summary_id: UUID, summary: AnyHttpUrl, db_url: str) -> None:
    await Tortoise.init(db_url=db_url, modules={"models": settings.MODELS})
    await Summary.filter(id=summary_id).update(summary=summary)


@celery.task(name="celery_generate_summary")
def celery_generate_summary(summary_id: UUID, url: AnyHttpUrl, db_url: str = settings.DATABASE_URL) -> Optional[bool]:
    article = Article(url, config=config)
    article.download()
    article.parse()
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    finally:
        article.nlp()
    summary = article.summary
    # Open a new connection on every update and close it automatically by run_async() helper.
    run_async(_update_summary(summary_id, summary, db_url))
    return True
