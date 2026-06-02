import pytest
from systemd_unit_builder.validator import validate_config

def test_valid_minimal():
    cfg = validate_config({"name": "test", "exec_start": "/usr/bin/app"})
    assert cfg.name == "test"

def test_invalid_missing_exec():
    with pytest.raises(ValueError):
        validate_config({"name": "bad"})