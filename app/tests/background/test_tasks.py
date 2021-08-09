# import shutil

# import pytest
# from celery.result import AsyncResult
# from tortoise import Tortoise

# from app.background.tasks import celery_generate_summary
# from app.config import get_settings
# from app.models import Summary, User
# from app.security.auth import create_password_hash
# from app.tests.conftest import TEST_USER

# settings = get_settings()


# @pytest.mark.asyncio
# async def test_celery_generate_summary():
#     try:
#         await Tortoise.init(db_url=settings.DATABASE_TEST_URL, modules={"models": settings.MODELS})
#         await Tortoise.generate_schemas()
#         try:
#             # Prepare a test state in case the nltk_data folder has already been created.
#             shutil.rmtree("/home/app/nltk_data")
#         except FileNotFoundError:
#             pass
#         user = User(
#             username=TEST_USER["username"],
#             email=TEST_USER["email"],
#             full_name=TEST_USER["full_name"],
#             hashed_password=create_password_hash(TEST_USER["password"]),
#         )
#         await user.save()
#         test_url = "https://lipsum.com/"
#         summary = Summary(url=test_url, summary="", user_id=user.id)
#         await summary.save()
#         task = celery_generate_summary.delay(summary.id, test_url, settings.DATABASE_TEST_URL)
#         task_result = AsyncResult(task.id)
#         while task_result.status == "PENDING":
#             task_result = AsyncResult(task.id)
#         assert task_result.status == "SUCCESS"
#         assert task_result.result is True
#         db_record = await Summary.filter(id=summary.id).first().values()
#         # Clean up DB after test by deleting the user and related summaries.
#         # await User.filter(id=user.id).delete()
#         assert "Lorem Ipsum" in db_record[0]["summary"]
#     finally:
#         await Tortoise.close_connections()
