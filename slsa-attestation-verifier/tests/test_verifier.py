import pytest
from slsa_attestation_verifier.verifier import verify_attestation

def test_valid_attestation(tmp_path):
    att = tmp_path / "att.json"
    att.write_text('{"payload": "test"}')
    result = verify_attestation(str(att), "sha256:abc")
    assert result.valid

def test_invalid_envelope(tmp_path):
    att = tmp_path / "att.json"
    att.write_text('{}')
    result = verify_attestation(str(att), "sha256:abc")
    assert not result.valid
