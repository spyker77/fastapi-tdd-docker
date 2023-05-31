import asyncio

import nltk
from newspaper import Article
from pydantic import AnyHttpUrl
from sqlalchemy import select

from app.database import async_session, get_settings
from app.models import Summary

from .worker import celery

settings = get_settings()

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


@celery.task(name="celery_generate_summary")
def celery_generate_summary(summary_id: int, url: AnyHttpUrl) -> None:
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    async def update_summary(summary_id: int, summary: str) -> None:
        async with async_session() as db:
            result = await db.execute(select(Summary).where(Summary.id == summary_id))
            summary_to_update = result.scalar_one()
            summary_to_update.summary = summary
            await db.commit()

    asyncio.run(update_summary(summary_id, article.summary))
