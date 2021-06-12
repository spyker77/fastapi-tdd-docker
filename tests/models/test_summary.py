import pytest
from tortoise import Tortoise

from app.config import get_settings
from app.models.summary import TextSummary

settings = get_settings()


@pytest.mark.asyncio
async def test_text_summary_str_method():
    test_url = "https://lipsum.com/"
    await Tortoise.init(db_url=settings.DATABASE_TEST_URL, modules={"models": settings.MODELS})
    await Tortoise.generate_schemas()
    summary = TextSummary(url=test_url, summary="")
    await summary.save()
    url = await TextSummary.filter(id=summary.id).first()
    await Tortoise.close_connections()
    assert str(url) == test_url
