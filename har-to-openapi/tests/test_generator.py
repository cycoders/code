from har_to_openapi.generator import group_endpoints, normalize_path, generate_openapi

SAMPLE_ENTRIES = [
    {
        "method": "GET",
        "host": "api.ex.com",
        "path": "/users/123",
        "query": "",
        "req_headers": {},
        "req_body": None,
        "resp_status": 200,
        "resp_body": {"id": 123, "name": "Alice"},
        "time": 150,
    },
    {
        "method": "GET",
        "host": "api.ex.com",
        "path": "/users/456",
        "resp_status": 200,
        "resp_body": {"id": 456, "name": "Bob"},
        "time": 160,
    },
]


def test_normalize_path():
    assert normalize_path("/users/123") == "/users/{id}"
    assert normalize_path("/projects/a1b2c3d4-e5f6-7890-abcd-ef1234567890") == "/projects/{uuid}"
    assert normalize_path("/static/file.txt") == "/static/file.txt"


def test_group_endpoints():
    endpoints = group_endpoints(SAMPLE_ENTRIES, min_samples=1)
    assert "/users/{id}" in endpoints
    assert "get" in endpoints["/users/{id}"]
    data = endpoints["/users/{id}"]["get"]
    assert data["samples"] == 2
    assert data["responses"]["200"]["properties"]["id"]["type"] == "integer"


def test_generate_openapi():
    endpoints = group_endpoints(SAMPLE_ENTRIES)
    spec = generate_openapi(endpoints)
    assert spec["openapi"] == "3.1.0"
    assert "/users/{id}" in spec["paths"]
    assert spec["servers"][0]["url"] == "https://api.ex.com"
