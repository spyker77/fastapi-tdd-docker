from typing import Optional

import nltk
from newspaper import Article
from pydantic import AnyUrl
from tortoise import Tortoise, run_async

from app.config import get_settings
from app.models.summary import TextSummary

from .worker import celery

settings = get_settings()


async def _update_summary(summary_id: int, summary: str, db_url: AnyUrl) -> None:
    await Tortoise.init(db_url=db_url, modules={"models": settings.MODELS})
    await TextSummary.filter(id=summary_id).update(summary=summary)


@celery.task(name="celery_generate_summary")
def celery_generate_summary(summary_id: int, url: str, db_url: AnyUrl = settings.DATABASE_URL) -> Optional[bool]:
    article = Article(url)
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


async def generate_summary(summary_id: int, url: str) -> None:
    article = Article(url)
    article.download()
    article.parse()
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    finally:
        article.nlp()
    summary = article.summary
    await TextSummary.filter(id=summary_id).update(summary=summary)
