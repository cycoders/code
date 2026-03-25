import json
from pathlib import Path
from http_cache_analyzer.har_parser import load_har_entries


def test_load_har_entries(tmp_path: Path):
    har_content = {
        "log": {
            "version": "1.2",
            "entries": [
                {
                    "request": {"url": "https://ex.com/test"},
                    "response": {"status": 200, "headers": [{"name": "cache-control", "value": "max-age=3600"}]},
                    "startedDateTime": "2023-01-01T00:00:00Z",
                }
            ],
        }
    }
    har_path = tmp_path / "test.har"
    with open(har_path, "w") as f:
        json.dump(har_content, f)

    entries = load_har_entries(har_path)
    assert len(entries) == 1
    assert entries[0].url == "https://ex.com/test"
    assert entries[0].cache_policy.max_age == 3600
