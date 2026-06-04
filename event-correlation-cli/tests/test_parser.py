from event_correlation_cli.parser import parse_logs
import json
import tempfile

def test_json_parsing():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        f.write(json.dumps({"ts": "2025-01-01T00:00:00Z", "id": 1}))
        f.flush()
        events = parse_logs([f.name])
        assert events[0]["id"] == 1