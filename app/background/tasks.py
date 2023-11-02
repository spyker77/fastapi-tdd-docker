import asyncio

from newspaper import Article
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session
from app.language_detection import LanguageDetector
from app.models import Summary
from app.summarization.summarizer import SummarizerFactory

from .worker import celery

settings = get_settings()

factory = SummarizerFactory()
detector = LanguageDetector()


@celery.task(name="celery_generate_summary")
def celery_generate_summary(summary_id: int, url: str) -> None:
    """Celery task to generate a summary for the given article URL.

    Args:
        summary_id (int): ID of the summary record in the database.
        url (str): URL of the article to summarize.
    """
    loop = asyncio.get_event_loop()

    # Download and parse the article.
    article = Article(url)
    article.download()
    article.parse()

    # Detect the language of the article text.
    lang = detector.detect(article.text)

    # Get the appropriate summarizer based on the detected language.
    summarizer = factory.get_summarizer(lang)

    # Generate the summary.
    summary = summarizer.summarize(article.text)

    async def update_summary(summary_id: int, summary: str) -> None:
        """Asynchronous function to update the summary record in the database.

        Args:
            summary_id (int): ID of the summary record in the database.
            summary (str): Generated summary text.
        """
        async with async_session() as db:
            result = await db.execute(select(Summary).where(Summary.id == summary_id))
            summary_to_update = result.scalar_one()
            summary_to_update.summary = summary
            await db.commit()

    # Run the asynchronous function to update the summary record.
    loop.run_until_complete(update_summary(summary_id, summary))
