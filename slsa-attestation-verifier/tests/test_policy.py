import pytest
from slsa_attestation_verifier.policy import load_policy, evaluate

def test_load_empty_policy():
    assert load_policy(None) == {}

def test_evaluate_passes():
    result = evaluate({"payload": {}}, "sha256:x", {})
    assert result.valid
