import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import base64

from .utils import safe_json_load

Entry = Dict[str, Any]

def parse_har(har_path: Path) -> List[Entry]:
    """Parse HAR file into normalized entries."""
    try:
        with har_path.open("r", encoding="utf-8") as f:
            har = json.load(f)
        if har.get("log", {}).get("creator", {}).get("name") not in ["mitmproxy", "browser"]:
            print(f"Warning: Unknown HAR creator: {har.get('log', {}).get('creator')}")
        entries = har["log"]["entries"]
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        raise ValueError(f"Invalid HAR file {har_path}: {e}")

    processed = []
    for entry in entries:
        req = entry.get("request", {})
        resp = entry.get("response", {})
        if not req or not resp:
            continue

        url_info = urlparse(req["url"])
        headers_req = {h["name"].lower(): h["value"] for h in req.get("headers", [])}
        headers_resp = {h["name"].lower(): h["value"] for h in resp.get("headers", [])}

        req_body = None
        post_data = req.get("postData", {})
        if post_data.get("mimeType") == "application/json" and post_data.get("text"):
            req_body = safe_json_load(post_data["text"])

        resp_body = None
        content = resp.get("content", {})
        if content.get("mimeType") == "application/json":
            text = content.get("text")
            if text:
                if content.get("encoding") == "base64":
                    text = base64.b64decode(text).decode("utf-8", errors="ignore")
                resp_body = safe_json_load(text)

        processed.append({
            "timestamp": entry["startedDateTime"],
            "method": req["method"],
            "host": url_info.netloc,
            "path": url_info.path,
            "query": url_info.query,
            "req_headers": headers_req,
            "req_body": req_body,
            "resp_status": resp["status"],
            "resp_headers": headers_resp,
            "resp_body": resp_body,
            "time": entry.get("time", 0),
        })
    return processed


def parse_har_files(har_files: List[Path]) -> List[Entry]:
    all_entries = []
    for f in har_files:
        all_entries.extend(parse_har(f))
    return all_entries
