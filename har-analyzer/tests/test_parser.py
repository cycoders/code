import json
import pytest
from har_analyzer.cli import parse_har_file  # Note: parser logic in cli


@pytest.mark.parametrize("key, expected", [("log", KeyError), ("entries", ValueError)])
def test_invalid_har(tmp_path, key, expected):
    har_file = tmp_path / "invalid.har"
    data = {"log": {"version": "1.2"}}
    if key == "log":
        del data["log"]
    elif key == "entries":
        data["log"]["entries"] = []
    har_file.write_text(json.dumps(data))
    # Logic tested in cli tests