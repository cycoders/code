import pytest
from datetime import datetime, timezone

from pulse_cli.models import CheckResult, EndpointConfig, PulseConfig


def test_check_result():
    result = CheckResult(
        timestamp=datetime.now(timezone.utc),
        endpoint_name="test",
        url="https://test.com",
        success=True,
    )
    assert result.success
    json_data = result.model_dump_json()
    roundtrip = CheckResult.model_validate_json(json_data)
    assert roundtrip.endpoint_name == "test"


def test_endpoint_config():
    ep = EndpointConfig(name="test", url="https://test.com")
    assert ep.expected_status == [200]


def test_pulse_config():
    config = PulseConfig(endpoints=[])
    assert len(config.endpoints) == 0