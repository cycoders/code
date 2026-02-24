import json
from pathlib import Path
from har_to_openapi.parser import parse_har

SAMPLE_HAR = {
    "log": {
        "entries": [
            {
                "request": {
                    "method": "GET",
                    "url": "https://api.ex.com/users/123",
                    "headers": [{"name": "Authorization", "value": "Bearer token"}],
                },
                "response": {
                    "status": 200,
                    "headers": [{"name": "Content-Type", "value": "application/json"}],
                    "content": {"mimeType": "application/json", "text": '{"id":123,"name":"Alice"}'},
                },
                "time": 150,
            },
            {
                "request": {
                    "method": "POST",
                    "url": "https://api.ex.com/users",
                    "postData": {"mimeType": "application/json", "text": '{"name":"Bob"}'},
                },
                "response": {"status": 201, "content": {"text": '{"id":456}'}},
                "time": 200,
            }
        ]
    }
}

def test_parse_har(tmp_path: Path):
    har_file = tmp_path / "sample.har"
    har_file.write_text(json.dumps(SAMPLE_HAR))
    entries = parse_har(har_file)
    assert len(entries) == 2
    assert entries[0]["method"] == "GET"
    assert entries[0]["host"] == "api.ex.com"
    assert entries[0]["path"] == "/users/123"
    assert entries[0]["resp_body"] == {"id": 123, "name": "Alice"}
    assert "authorization" in entries[0]["req_headers"]
