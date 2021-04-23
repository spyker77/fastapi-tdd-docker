from tortoise import Tortoise, run_async

from app.main import MODELS
from init_db import generate_schema


def test_generate_schema():
    run_async(generate_schema())
    generated_schema = Tortoise.describe_models()
    assert len(generated_schema) == len(MODELS)
