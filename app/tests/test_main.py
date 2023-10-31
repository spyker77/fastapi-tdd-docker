import logging

import pytest
from fastapi import FastAPI

from app.main import lifespan


@pytest.mark.asyncio
async def test_lifespan_logging(caplog):
    caplog.set_level(logging.INFO)
    app = FastAPI()

    async with lifespan(app):
        assert "Starting up..." in caplog.text

    assert "Shutting down..." in caplog.text
