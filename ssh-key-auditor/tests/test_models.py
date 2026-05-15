from ssh_key_auditor.models import Severity, KeyInfo, Issue


def test_severity_enum():
    assert Severity.CRITICAL.value == "CRITICAL"


def test_keyinfo_dataclass():
    ki = KeyInfo("rsa", 2048, "P-256", "01:23:..", "user@host")
    assert ki.key_type == "rsa"
    assert ki.size_bits == 2048