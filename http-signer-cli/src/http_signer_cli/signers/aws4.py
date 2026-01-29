import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, quote
from typing import Dict, Optional

_RE_SPACE = re.compile(r"\s+")

def _canonical_header_value(value: str) -> str:
    return _RE_SPACE.sub(" ", value).strip()

def _prep_signing_key(secret: str, dt: datetime, region: str, service: str) -> bytes:
    def _hmac(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    date_key = _hmac(f"AWS4{secret}".encode("utf-8"), dt.strftime("%Y%m%d"))
    region_key = _hmac(date_key, region)
    service_key = _hmac(region_key, service)
    return _hmac(service_key, "aws4_request")

def sign_aws4(
    method: str,
    url: str,
    headers: Dict[str, str],
    body: bytes,
    access_key: str,
    secret_key: str,
    region: str,
    service: str,
    session_token: Optional[str] = None,
) -> Dict[str, str]:
    """Sign request with AWS SigV4. Returns full signed headers."""
    dt = datetime.now(timezone.utc)
    timestamp = dt.strftime("%Y%m%dT%H%M%SZ")

    parsed_url = urlparse(url)
    can_uri = parsed_url.path if parsed_url.path else "/"
    can_query = ""
    if parsed_url.query:
        qs = parse_qs(parsed_url.query)
        can_query = "&".join(f"{quote(k, safe='~')}={quote(vs[0] if isinstance(vs, list) else vs, safe='~')}" for k, vs in sorted(qs.items()))

    payload_hash = hashlib.sha256(body).hexdigest()

    signing_headers = headers.copy()
    signing_headers["host"] = parsed_url.netloc
    signing_headers["x-amz-date"] = timestamp
    signing_headers["x-amz-content-sha256"] = payload_hash
    if session_token:
        signing_headers["x-amz-security-token"] = session_token

    def key_lower(k: str) -> str:
        return k.lower().strip()

    sorted_headers = sorted((key_lower(k), signing_headers[k]) for k in signing_headers)
    can_headers = "\n".join(f"{k}:{_canonical_header_value(v)}\n" for k, v in sorted_headers)
    signed_hdrs_str = ";".join(k for k, _ in sorted_headers)

    can_request = f"{method}\n{can_uri}\n{can_query}\n{can_headers}{signed_hdrs_str}\n{payload_hash}"
    can_request_hash = hashlib.sha256(can_request.encode("utf-8")).hexdigest()

    scope = f"{dt.strftime('%Y%m%d')}/{region}/{service}/aws4_request"
    string_to_sign = f"AWS4-HMAC-SHA256\n{timestamp}\n{scope}\n{can_request_hash}"

    signing_key = _prep_signing_key(secret_key, dt, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    credential = f"{access_key}/{scope}"
    auth = (
        f"AWS4-HMAC-SHA256 Credential={credential},"
        f"SignedHeaders={signed_hdrs_str},Signature={signature}"
    )
    signing_headers["Authorization"] = auth

    return signing_headers