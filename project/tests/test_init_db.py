import os

from tortoise import Tortoise, run_async

from app.main import MODELS
from init_db import generate_schema


def test_generate_schema():
    db_url = os.environ.get("DATABASE_TEST_URL")
    run_async(generate_schema(db_url))
    generated_schema = Tortoise.describe_models()
    assert len(generated_schema) == len(MODELS)
