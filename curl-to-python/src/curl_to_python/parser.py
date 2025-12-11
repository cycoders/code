'''Parser for curl command-line arguments.'''

import json
import shlex
import warnings
from typing import Optional

from urllib.parse import parse_qsl

from .models import CurlParsed


def parse_curl(curl_command: str) -> CurlParsed:
    """Parse a curl command string into a structured CurlParsed object."""

    args = shlex.split(curl_command)
    if not args or args[0].lower() != "curl":
        raise ValueError("Must start with 'curl'")

    args = args[1:]
    parsed = CurlParsed()
    data_args: list[str] = []
    form_args: list[str] = []
    i = 0

    while i < len(args):
        arg = args[i]

        if not arg.startswith("-"):
            if not parsed.url:
                parsed.url = arg
            i += 1
            continue

        # Method
        if arg in ("-X", "--request"):
            parsed.method = args[i + 1]
            i += 2
            continue
        if arg.startswith("-X"):
            parsed.method = arg[2:]
            i += 1
            continue

        # Headers
        if arg in ("-H", "--header"):
            header_str = args[i + 1]
            if ":" not in header_str:
                warnings.warn(f"Skipping invalid header: {header_str}")
                i += 2
                continue
            key, value = header_str.split(":", 1)
            parsed.headers[key.strip()] = value.strip()
            i += 2
            continue
        if arg.startswith("-H"):
            header_str = arg[2:]
            if ":" not in header_str:
                warnings.warn(f"Skipping invalid header: {header_str}")
                i += 1
                continue
            key, value = header_str.split(":", 1)
            parsed.headers[key.strip()] = value.strip()
            i += 1
            continue

        # Data
        if arg in ("-d", "--data", "--data-raw", "--data-binary", "--data-urlencode"):
            if len(arg) > 2 and arg.startswith("-d"):
                data_args.append(arg[2:])
            else:
                data_args.append(args[i + 1])
            i += 2
            continue
        if arg.startswith("-d") and len(arg) > 2:
            data_args.append(arg[2:])
            i += 1
            continue

        # Forms/Files
        if arg in ("-F", "--form"):
            if len(arg) > 3 and arg.startswith("-F"):
                form_args.append(arg[3:])
            else:
                form_args.append(args[i + 1])
            i += 2
            continue
        if arg.startswith("-F") and len(arg) > 3:
            form_args.append(arg[3:])
            i += 1
            continue

        # Auth
        if arg in ("-u", "--user"):
            auth_str = args[i + 1]
            if ":" in auth_str:
                parsed.auth_user, parsed.auth_pass = auth_str.split(":", 1)
            else:
                parsed.auth_user = auth_str
            i += 2
            continue
        if arg.startswith("-u"):
            auth_str = arg[2:]
            if ":" in auth_str:
                parsed.auth_user, parsed.auth_pass = auth_str.split(":", 1)
            else:
                parsed.auth_user = auth_str
            i += 1
            continue

        # GET params
        if arg in ("-G", "--get"):
            parsed.is_get = True
            i += 1
            continue

        # Warn unknown
        if arg.startswith("--") or arg.startswith("-"):
            warnings.warn(f"Unsupported flag ignored: {arg}")
        i += 1

    # Process data
    if data_args:
        parsed.data = " ".join(data_args)

    # Process forms
    for farg in form_args:
        if "=" not in farg:
            continue
        k, v = farg.split("=", 1)
        if v.startswith("@"):
            parsed.files[k] = v[1:]
        else:
            parsed.form_data[k] = v

    # Handle GET params
    if parsed.is_get and parsed.data:
        qpairs = parse_qsl(parsed.data)
        for k, v in qpairs:
            parsed.params[k] = v
        parsed.data = ""

    # Infer JSON
    if parsed.data:
        try:
            parsed.json_data = json.loads(parsed.data)
            ct = parsed.headers.get("Content-Type", "")
            if "json" not in ct.lower():
                parsed.headers["Content-Type"] = "application/json"
            parsed.data = ""
        except json.JSONDecodeError:
            pass

    if not parsed.url:
        raise ValueError("No URL found")

    if not parsed.method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
        warnings.warn(f"Unknown method {parsed.method}, defaulting to GET")
        parsed.method = "GET"

    return parsed
