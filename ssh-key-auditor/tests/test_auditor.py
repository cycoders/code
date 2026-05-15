import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from ssh_key_auditor.auditor import scan_ssh_dir, check_permissions
from ssh_key_auditor.models import Severity


def test_weak_rsa_detection(sample_ssh_dir, mock_key_rsa_weak):
    pub_file = sample_ssh_dir / "id_rsa.pub"
    pub_file.write_text("ssh-rsa weakkeydata comment")

    with patch(
        "cryptography.hazmat.primitives.serialization.load_ssh_public_key",
        return_value=mock_key_rsa_weak,
    ):
        issues = scan_ssh_dir(sample_ssh_dir)
        weak_issues = [i for i in issues if "WEAK_RSA_SIZE" in i.issue_type]
        assert len(weak_issues) == 1
        assert weak_issues[0].severity == Severity.CRITICAL


def test_good_ed25519(sample_ssh_dir, mock_key_ed25519):
    pub_file = sample_ssh_dir / "id_ed25519.pub"
    pub_file.write_text("ssh-ed25519 gooddata")

    with patch(
        "cryptography.hazmat.primitives.serialization.load_ssh_public_key",
        return_value=mock_key_ed25519,
    ):
        issues = scan_ssh_dir(sample_ssh_dir)
        assert len(issues) == 0


def test_bad_permissions(sample_ssh_dir):
    priv_file = sample_ssh_dir / "id_rsa"
    priv_file.write_text("private")
    priv_file.chmod(0o666)

    issues = scan_ssh_dir(sample_ssh_dir)
    perm_issues = [i for i in issues if "BAD_PERMS_PRIVATE" in i.issue_type]
    assert len(perm_issues) == 1


def test_orphan_private(sample_ssh_dir):
    priv_file = sample_ssh_dir / "orphan"
    priv_file.write_text("orphan")

    issues = scan_ssh_dir(sample_ssh_dir)
    orphan_issues = [i for i in issues if i.issue_type == "ORPHAN_PRIVATE"]
    assert len(orphan_issues) == 1


def test_duplicate_fp(sample_ssh_dir, mock_key_rsa_weak):
    pub1 = sample_ssh_dir / "dup1.pub"
    pub2 = sample_ssh_dir / "dup2.pub"
    pub1.write_text("ssh-rsa dupdata")
    pub2.write_text("ssh-rsa dupdata")

    with patch(
        "cryptography.hazmat.primitives.serialization.load_ssh_public_key",
        return_value=mock_key_rsa_weak,
    ):
        issues = scan_ssh_dir(sample_ssh_dir)
        dup_issues = [i for i in issues if i.issue_type == "DUPLICATE_FP"]
        assert len(dup_issues) == 2