import secrets
import base64
import hashlib
from typing import Tuple


def generate_state() -> str:
    """Generate cryptographically secure state parameter."""
    return secrets.token_urlsafe(32)


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE verifier and challenge pair."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
    return verifier, challenge
