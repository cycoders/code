import hmac
import hashlib
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import parse_qs

import hmac

from fastapi import Request, HTTPException

SUPPORTED_PROVIDERS = {
    "github": "x-hub-signature-256",
    "stripe": "stripe-signature",
    "slack": "x-slack-signature",
    "gitlab": "x-gitlab-token",
    "discord": "x-signature-ed25519",
}

class SignatureVerifier:
    @staticmethod
    def verify_github(payload: bytes, signature: str, secret: str) -> bool:
        expected = f"sha256={hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()}"
        return hmac.compare_digest(signature, expected)

    @staticmethod
    def verify_stripe(payload: bytes, signature: str, secret: str, tolerance: int = 300) -> bool:
        try:
            sigs = dict(q.split('=', 1) for q in signature.split(','))
            timestamp = int(sigs['t'])
            if abs(time.time() - timestamp) > tolerance:
                return False
            m = f"t={timestamp}.{payload.decode()}"
            expected = f"v1={hmac.new(secret.encode(), m.encode(), hashlib.sha256).hexdigest()}"
            return hmac.compare_digest(sigs.get('v1', ''), expected.split('=', 1)[1])
        except:
            return False

    @staticmethod
    def verify_slack(payload: bytes, signature: str, secret: str) -> bool:
        expected = f"v0={hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()}"
        return hmac.compare_digest(signature, expected)

    @staticmethod
    def verify_generic(payload: bytes, signature: str, secret: str, algo: str = 'sha256') -> bool:
        h = hashlib.new(algo)
        h.update(secret.encode())
        h.update(payload)
        expected = h.hexdigest()
        return hmac.compare_digest(signature, expected)

    @staticmethod
    def detect_and_verify(
        request: Request, endpoint_secret: str
    ) -> Tuple[bool, str]:
        payload = request.body()
        headers = dict(request.headers)

        provider = "unknown"
        for p, h in SUPPORTED_PROVIDERS.items():
            sig = headers.get(h)
            if sig:
                provider = p
                break

        if not sig or not endpoint_secret:
            return False, "no_sig"

        verifiers = {
            "github": lambda: SignatureVerifier.verify_github(payload, sig, endpoint_secret),
            "stripe": lambda: SignatureVerifier.verify_stripe(payload, sig, endpoint_secret),
            "slack": lambda: SignatureVerifier.verify_slack(payload, sig, endpoint_secret),
            # Add more
        }

        if provider in verifiers:
            verified = verifiers[provider]()
            return verified, provider

        # Generic HMAC
        return SignatureVerifier.verify_generic(payload, sig.replace("sha256=", ""), endpoint_secret), "hmac"
