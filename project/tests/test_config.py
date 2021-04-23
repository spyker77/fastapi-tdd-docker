import logging

from app.config import get_settings


def test_get_settings_logging(caplog):
    caplog.set_level(logging.INFO)
    get_settings()
    assert "Loading config settings from the environment..." in caplog.text
