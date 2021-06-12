from tortoise import Tortoise, run_async

from app.config import get_settings
from init_db import generate_schema

settings = get_settings()


def test_generate_schema():
    db_url = settings.DATABASE_TEST_URL
    run_async(generate_schema(db_url))
    generated_schema = Tortoise.describe_models()
    assert len(generated_schema) == len(settings.MODELS)
