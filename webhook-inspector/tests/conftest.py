import pytest
from httpx import AsyncClient
from pathlib import Path

from webhook_inspector.app import create_app
from webhook_inspector.config import Config, EndpointConfig
from webhook_inspector.storage import Storage

@pytest.fixture
async def app():
    cfg = Config(endpoints={"/test": EndpointConfig(secret="test")}, storage=StorageConfig(dir=Path("test_logs")))
    storage = Storage(cfg.storage_dir)
    yield create_app(cfg, storage)
