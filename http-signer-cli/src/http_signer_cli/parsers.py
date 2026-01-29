import shlex
import re
from typing import Dict

def parse_curl(curl_line: str) -> Dict[str, str]:
    """Parse simple curl command to request dict. Supports -X, -H, -d."""
    parts = shlex.split(curl_line)
    if parts[0] != "curl":
        raise ValueError("Invalid curl command")

    args = parts[1:]
    method = "GET"
    url = None
    headers = {}
    body = ""

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-X" or arg == "--request":
            method = args[i + 1]
            i += 2
            continue
        elif arg in ("-H", "--header"):
            i += 1
            if i < len(args):
                h = args[i]
                if ":" in h:
                    k, v = h.split(":", 1)
                    headers[k.strip()] = v.strip()
                i += 1
            continue
        elif arg in ("-d", "--data", "--data-raw"):
            i += 1
            if i < len(args):
                body = args[i]
            i += 1
            continue
        elif not arg.startswith("-"):
            url = arg
        i += 1

    if url is None:
        raise ValueError("No URL in curl command")

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "body": body,
    }