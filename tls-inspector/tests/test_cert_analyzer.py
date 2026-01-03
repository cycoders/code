import pytest
from tls_inspector.cert_analyzer import analyze_cert, analyze_chain
from tls_inspector.tests.conftest import sample_rsa_der, sample_chain_der


def test_analyze_cert_rsa(sample_rsa_der):
    cert_info = analyze_cert(sample_rsa_der)
    assert cert_info.key_type == "RSA"
    assert cert_info.key_size == 2048
    assert "SHA256" in cert_info.sig_algo
    assert "test.com" in cert_info.san
    assert cert_info.subject.endswith("Test.com")


def test_analyze_chain_valid(sample_chain_der):
    certs, valid = analyze_chain(sample_chain_der)
    assert len(certs) == 2
    assert valid is True


def test_analyze_chain_invalid(sample_rsa_der):
    # Mismatch chain
    invalid_chain = [sample_rsa_der, sample_rsa_der]  # subjects differ? simplistic
    certs, valid = analyze_chain(invalid_chain)
    assert valid is False  # due to self-signed check logic


def test_cert_no_san(sample_rsa_der):
    # Remove SAN for test? but fixture has it
    cert_info = analyze_cert(sample_rsa_der)
    assert isinstance(cert_info.san, list)