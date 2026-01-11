from datetime import datetime, timezone

import pytest
from rate_limit_tester.models import RateLimitInfo


@pytest.fixture
def info():
    return RateLimitInfo(
        limit=60,
        remaining=30,
        reset_timestamp=int(datetime.now(tz=timezone.utc).timestamp()) + 3600,
    )


def test_model_computed(info: RateLimitInfo):
    assert info.percentage_used == 50.0
    assert info.reset_seconds > 3500


def test_rich_table(info: RateLimitInfo):
    table = info.rich_table()
    assert "Limit" in str(table)
