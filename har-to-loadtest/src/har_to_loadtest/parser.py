import json
from pathlib import Path
from typing import List

from .model import HttpRequest


def parse_har(har_path: str) -> List[HttpRequest]:
    """Parse HAR file into list of HttpRequest objects.\n\n    Raises:\n        FileNotFoundError: If file not found.\n        KeyError: Invalid HAR structure.\n        ValueError: Unsupported version.\n    """
    path = Path(har_path)
    if not path.is_file():
        raise FileNotFoundError(f"HAR file not found: {har_path}")

    with open(har_path, "r", encoding="utf-8") as f:
        har_data = json.load(f)

    log = har_data.get("log")
    if not log:
        raise KeyError("'log' key")
    if log.get("version") != "1.2":
        raise ValueError(f"Unsupported HAR version: {log.get('version')}")

    entries = log.get("entries", [])
    requests: List[HttpRequest] = []

    for entry in entries:
        req_data = entry.get("request")
        if not req_data:
            continue  # Skip invalid entries

        method = req_data["method"]
        url = req_data["url"]
        headers_list = req_data.get("headers", [])
        headers = {h["name"].lower(): h["value"] for h in headers_list if "name" in h and "value" in h}

        post_data = req_data.get("postData", {})
        body = post_data.get("text")
        json_body = None

        if body:
            try:
                json_body = json.loads(body)
                headers["content-type"] = headers.get("content-type", "application/json")
            except json.JSONDecodeError:
                json_body = None

        requests.append(HttpRequest(
            method=method,
            url=url,
            headers=headers,
            body=body,
            json_body=json_body,
        ))

    return requests
