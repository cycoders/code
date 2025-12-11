'''Renderer for generating Python code from parsed curl.''' 

from typing import Dict, Any

import json

from .models import CurlParsed


def dict_to_literal(d: Dict[str, Any]) -> str:
    """Convert dict to pretty Python literal."""
    if not d:
        return "{}"
    items = [f'    {repr(k)}: {repr(v)}' for k, v in d.items()]
    return "{\n" + ",\n".join(items) + "\n}"


def parsed_to_code(parsed: CurlParsed, httpx: bool = False, async_: bool = False) -> str:
    """Generate Python code from parsed curl."""

    client = "httpx" if httpx else "requests"
    is_async = async_ and httpx

    imports = [client]
    auth_import = ""

    # Auth
    auth_str = ""
    if parsed.auth_user:
        user = repr(parsed.auth_user)
        password = repr(parsed.auth_pass) if parsed.auth_pass else 'None'
        auth_str = f", auth=({user}, {password})"

    # Headers
    headers_str = dict_to_literal(parsed.headers)
    headers_kw = "headers=headers,\n" if parsed.headers else ""

    # Params
    params_str = ""
    if parsed.params:
        params_str = f"params={dict_to_literal(parsed.params)},\n"

    # Body
    body_kwargs = []
    if parsed.json_data:
        body_kwargs.append(f"json={dict_to_literal(parsed.json_data)}")
    if parsed.data:
        body_kwargs.append(f"data={repr(parsed.data)}")
    if parsed.form_data:
        body_kwargs.append(f"data={dict_to_literal(parsed.form_data)}")
    if parsed.files:
        files_items = [
            f'{repr(k)}: ("{v}", open("{v}", "rb"))'
            for k, v in sorted(parsed.files.items())
        ]
        files_dict = "{\n" + ",\n".join(f"    {item}" for item in files_items) + "\n}"
        body_kwargs.append(f"files={files_dict}")

    body_str = "\n    ".join(body_kwargs) if body_kwargs else ""
    body_str = f",\n    {body_str}" if body_str else ""

    # Method call
    method = parsed.method.lower()
    if is_async:
        call_prefix = "await client."
        client_ctx = "async with httpx.AsyncClient() as client:\n    "
    elif httpx:
        call_prefix = "httpx."
        client_ctx = ""
    else:
        call_prefix = "requests."
        client_ctx = ""

    code = f"""import {', '.join(imports)}{auth_import}

headers = {headers_str}

{client_ctx}response = {call_prefix}{method}(
    "{parsed.url}",
{headers_kw}{params_str}{body_str}{auth_str}
)

response.raise_for_status()
print(response.json())
"""

    return code.rstrip()
