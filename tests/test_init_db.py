from tortoise import Tortoise, run_async

from app.config import MODELS, get_settings
from init_db import generate_schema


def test_generate_schema():
    db_url = get_settings().database_test_url
    run_async(generate_schema(db_url))
    generated_schema = Tortoise.describe_models()
    assert len(generated_schema) == len(MODELS)
