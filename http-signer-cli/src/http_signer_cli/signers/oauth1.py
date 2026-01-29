import hashlib
import hmac
import time
import os
import base64
import secrets
from urllib.parse import urlparse, parse_qs, quote
from typing import Dict, Optional

_OAUTH_PARAMS_ORDER = [
    "oauth_consumer_key",
    "oauth_nonce",
    "oauth_signature_method",
    "oauth_timestamp",
    "oauth_token",
    "oauth_version",
    "oauth_signature",
]

def sign_oauth1(
    method: str,
    url: str,
    headers: Dict[str, str],
    body: bytes,
    consumer_key: str,
    consumer_secret: str,
    access_token: Optional[str] = None,
    token_secret: Optional[str] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """Sign request with OAuth 1.0a. Returns headers with Authorization."""
    parsed_url = urlparse(url)
    can_uri = parsed_url.path or "/"

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
    }
    if access_token:
        oauth_params["oauth_token"] = access_token

    # Query params
    query_params = parse_qs(parsed_url.query or "", keep_blank_values=True)
    all_params = {**{k: v[0] if isinstance(v, list) else v for k, v in query_params.items()}, **oauth_params}

    sorted_param_items = sorted(all_params.items())
    can_params = "&".join(f"{quote(k, safe='~')}={quote(v, safe='~')}" for k, v in sorted_param_items)

    base_string = f"{method}&{quote(can_uri, safe='~')}&{quote(can_params, safe='~')}"

    key = f"{quote(consumer_secret, safe='~')}&{quote(token_secret or '', safe='~')}"
    sig_bytes = hmac.new(key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha256).digest()
    oauth_params["oauth_signature"] = base64.b64encode(sig_bytes).decode("utf-8")

    # Auth header
    auth_parts = []
    if realm:
        auth_parts.append(f'realm="{quote(realm, safe="~")}"')
    auth_parts += [f'{k}="{quote(v, safe="~")}" ' for k, v in sorted(oauth_params.items())]
    auth_header = "OAuth " + ",".join(auth_parts).rstrip(", ")

    headers["Authorization"] = auth_header
    return headers