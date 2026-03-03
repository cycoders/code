import pytest
from httpx import Response
from pytest_httpx import HTTPXMock

@pytest.fixture(autouse=True)
def cleanups(monkeypatch):
    monkeypatch.setenv("CORS_AUDITOR_TIMEOUT", "10")