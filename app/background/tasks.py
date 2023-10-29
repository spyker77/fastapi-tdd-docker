import asyncio

from newspaper import Article
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session
from app.models import Summary
from app.summarization.summarizer import Summarizer

from .worker import celery

settings = get_settings()


@celery.task(name="celery_generate_summary")
def celery_generate_summary(summary_id: int, url: str) -> None:
    loop = asyncio.get_event_loop()

    article = Article(url)
    article.download()
    article.parse()

    summary = Summarizer.summarize(article.text, settings.SUMMARIZER_MODEL)

    async def update_summary(summary_id: int, summary: str) -> None:
        async with async_session() as db:
            result = await db.execute(select(Summary).where(Summary.id == summary_id))
            summary_to_update = result.scalar_one()
            summary_to_update.summary = summary
            await db.commit()

    loop.run_until_complete(update_summary(summary_id, summary))
