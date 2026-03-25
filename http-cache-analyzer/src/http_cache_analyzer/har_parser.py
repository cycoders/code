import json
from pathlib import Path
from datetime import datetime

from .models import HttpResponse

from .cache_parser import parse_cache_policy


def load_har_entries(har_path: Path) -> list[HttpResponse]:
    """Load and parse HAR file into HttpResponse list."""
    try:
        with open(har_path, 'r') as f:
            har = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        raise ValueError(f"Invalid HAR file {har_path}: {e}")

    if har.get('log', {}).get('version') != 1.2:
        raise ValueError("Only HAR 1.2 supported")

    entries = []
    base_time = None

    for entry in har['log']['entries']:
        req = entry['request']
        resp = entry['response']

        resp_headers = {}
        for h in resp.get('headers', []):
            name = h['name'].lower()
            resp_headers[name] = h['value']

        started = entry.get('startedDateTime')
        ts = datetime.fromisoformat(started.replace('Z', '+00:00')) if started else None
        if base_time is None and ts:
            base_time = ts

        hr = HttpResponse(
            url=req['url'],
            status_code=resp['status'],
            headers=resp_headers,
            timestamp=ts
        )
        hr.cache_policy = parse_cache_policy(resp_headers)
        entries.append(hr)

    return entries
