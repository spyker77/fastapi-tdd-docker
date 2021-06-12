import shutil

import pytest
from celery.result import AsyncResult

from app.background.tasks import celery_generate_summary
from app.models.summary import TextSummary

from .conftest import get_settings_override

db_url = get_settings_override().DATABASE_URL


@pytest.mark.asyncio
async def test_celery_generate_summary(test_app_with_db):
    try:
        # Prepare a test state in case the nltk_data folder has already been created.
        shutil.rmtree("/home/app/nltk_data")
    except FileNotFoundError:
        pass
    url = "https://lipsum.com/"
    summary = TextSummary(url=url, summary="")
    await summary.save()
    task = celery_generate_summary.delay(summary.id, url, db_url)
    task_result = AsyncResult(task.id)
    while task_result.status == "PENDING":
        task_result = AsyncResult(task.id)
    assert task_result.status == "SUCCESS"
    assert task_result.result is True
    db_record = await TextSummary.filter(id=summary.id).first().values()
    assert "Lorem Ipsum" in db_record[0]["summary"]


def test_generate_summary(test_app_with_db):
    try:
        # Prepare a test state in case the nltk_data folder has already been created.
        shutil.rmtree("/home/app/nltk_data")
    except FileNotFoundError:
        pass
    response = test_app_with_db.post(
        url="/api/v1/summaries/",
        json={"url": "https://lipsum.com/"},
        headers={"Content-Type": "application/json"},
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.get(f"/api/v1/summaries/{summary_id}/")
    assert "Lorem Ipsum" in response.json()["summary"]
