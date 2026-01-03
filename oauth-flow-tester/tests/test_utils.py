import pytest
from oauth_flow_tester.utils import generate_state, generate_pkce_pair
import hashlib
import base64


def test_generate_state_length():
    state = generate_state()
    assert len(state) >= 32
    assert "=" not in state


def test_pkce_challenge_matches_verifier():
    verifier, challenge = generate_pkce_pair()
    hashed = hashlib.sha256(verifier.encode()).digest()
    expected = base64.urlsafe_b64encode(hashed).decode().rstrip("=")
    assert challenge == expected
    assert len(verifier) == 43  # Standard length
