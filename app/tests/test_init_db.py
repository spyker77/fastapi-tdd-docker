from tortoise import Tortoise, run_async

from app import models
from app.config import get_settings
from init_db import generate_schema

settings = get_settings()


def test_generate_schema():
    db_url = settings.DATABASE_TEST_URL
    run_async(generate_schema(db_url))
    generated_schema = Tortoise.describe_models()
    # Get all the class names from the models module.
    app_models = [class_name for class_name, cls in models.__dict__.items() if isinstance(cls, type)]
    for model_name in generated_schema.keys():
        # Aerich is not an app's model and should be used by default, therefore skip.
        if model_name != "models.Aerich":
            assert model_name.split(".")[-1] in app_models
