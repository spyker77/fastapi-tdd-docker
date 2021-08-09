import logging

from app.config import get_settings


def test_get_settings_logging(caplog):
    caplog.set_level(logging.INFO)
    # Clear the cache first due to using the lru_cache decorator and then call.
    get_settings.cache_clear()
    get_settings()
    assert "Loading config settings from the environment..." in caplog.text
