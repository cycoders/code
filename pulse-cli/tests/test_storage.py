import pytest
from datetime import datetime, timedelta

from pulse_cli.storage import Storage
from pulse_cli.models import CheckResult


def test_storage(tmp_storage):
    result = CheckResult(
        timestamp=datetime.now(),
        endpoint_name="test",
        url="https://test.com",
        success=True,
    )
    tmp_storage.store(result)

    checks = tmp_storage.get_checks("test", limit=10)
    assert len(checks) == 1
    assert checks[0].endpoint_name == "test"
    assert checks[0].success


def test_latest_per_endpoint(tmp_storage):
    for i in range(2):
        result = CheckResult(
            timestamp=datetime.now() - timedelta(hours=i),
            endpoint_name="ep1",
            url="https://test.com",
            success=bool(i),
        )
        tmp_storage.store(result)
    results = tmp_storage.get_latest_per_endpoint()
    assert len(results) == 1
    assert results[0].success