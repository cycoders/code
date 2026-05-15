import base64
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Set

import cryptography
cryptography.hazmat.backends.openssl.backend  # noqa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, dsa

from .models import KeyInfo, Issue, Severity


def compute_fingerprint(key: serialization.PublicKeyTypes) -> str:
    key_bytes = key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(key_bytes)
    fp_bytes = digest.finalize()
    return ":".join(f"{b:02x}" for b in fp_bytes)


def analyze_key(key_type: str, key: serialization.PublicKeyTypes) -> List[str]:
    issues = []
    fp = compute_fingerprint(key)

    if key_type == "ssh-rsa":
        size = key.public_numbers().n.bit_length()
        ki = KeyInfo("rsa", size, None, fp, None)
        if size < 2048:
            issues.append("WEAK_RSA_SIZE")
        if size < 3072:
            issues.append("RSA_NOT_PREFERRED")
    elif key_type == "ssh-dss":
        ki = KeyInfo("dss", None, None, fp, None)
        issues.append("DEPRECATED_DSS")
    elif key_type.startswith("ecdsa-sha2-"):
        curve_name = key_type.split("-")[-1].upper()
        ki = KeyInfo("ecdsa", None, curve_name, fp, None)
        if curve_name == "NISTP256":  # P-256
            pass  # ok
        elif curve_name == "NISTP384":
            pass
        elif curve_name == "NISTP521":
            pass
        else:
            issues.append("WEAK_EC_CURVE")
    elif key_type == "ssh-ed25519":
        ki = KeyInfo("ed25519", None, None, fp, None)
    elif key_type.startswith("sk-"):
        ki = KeyInfo(key_type, None, None, fp, None)
    else:
        ki = KeyInfo(key_type, None, None, fp, None)
        issues.append("UNKNOWN_KEY_TYPE")

    return issues, ki


def scan_ssh_dir(dir_path: Path) -> List[Issue]:
    issues: List[Issue] = []
    fingerprints: Dict[str, List[str]] = {}
    private_keys = set()
    pub_suffixes = set()

    # Collect private keys
    for p in dir_path.glob("id_*"):
        if not p.suffix == ".pub":
            private_keys.add(p.stem)
            check_permissions(p, issues, "private")

    # Collect .pub files
    for p in dir_path.glob("*.pub"):
        pub_suffixes.add(p.stem)
        check_permissions(p, issues, "public")
        parse_pub_file(p, issues, fingerprints)

    # authorized_keys
    auth_file = dir_path / "authorized_keys"
    if auth_file.exists():
        check_permissions(auth_file, issues, "authorized_keys")
        parse_pub_file(auth_file, issues, fingerprints)

    # Orphans
    for priv in private_keys - pub_suffixes:
        priv_path = dir_path / priv
        issues.append(
            Issue(
                file_path=str(priv_path),
                line_num=0,
                key_info=KeyInfo("unknown", None, None, "", ""),
                issue_type="ORPHAN_PRIVATE",
                message="Private key without matching .pub file",
                severity=Severity.MEDIUM,
            )
        )

    # Duplicates
    for fp, files in fingerprints.items():
        if len(files) > 1:
            for f in files:
                issues.append(
                    Issue(
                        file_path=f,
                        line_num=0,
                        key_info=KeyInfo("dup", None, None, fp, ""),
                        issue_type="DUPLICATE_FP",
                        message=f"Duplicate fingerprint (appears {len(files)} times)",
                        severity=Severity.MEDIUM,
                    )
                )

    return issues


def parse_pub_file(file_path: Path, issues: List[Issue], fingerprints: Dict[str, List[str]]):
    try:
        lines = file_path.read_text().splitlines()
    except Exception:
        issues.append(
            Issue(
                str(file_path),
                0,
                KeyInfo("", None, None, "", ""),
                "UNREADABLE_FILE",
                "Could not read file",
                Severity.LOW,
            )
        )
        return

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = line.split()
            if len(parts) < 2:
                continue
            key_type = parts[0]
            key_data = " ".join(parts[1:]).encode()
            key = serialization.load_ssh_public_key(key_data)
            key_issues, ki = analyze_key(key_type, key)
            ki.comment = parts[-1] if len(parts) > 2 else None

            for issue_type in key_issues:
                sev = {
                    "DEPRECATED_DSS": Severity.CRITICAL,
                    "WEAK_RSA_SIZE": Severity.CRITICAL,
                    "RSA_NOT_PREFERRED": Severity.HIGH,
                    "WEAK_EC_CURVE": Severity.HIGH,
                    "UNKNOWN_KEY_TYPE": Severity.LOW,
                }.get(issue_type, Severity.MEDIUM)
                msg = {
                    "DEPRECATED_DSS": "DSA is deprecated and insecure",
                    "WEAK_RSA_SIZE": f"RSA key too small (<2048 bits)",
                    "RSA_NOT_PREFERRED": "RSA <3072 bits; prefer Ed25519",
                    "WEAK_EC_CURVE": "Unsupported EC curve",
                    "UNKNOWN_KEY_TYPE": "Unknown key type",
                }.get(issue_type, "Potential issue")
                issues.append(
                    Issue(
                        file_path=str(file_path),
                        line_num=i,
                        key_info=ki,
                        issue_type=issue_type,
                        message=msg,
                        severity=sev,
                    )
                )

            fp = ki.fingerprint
            fingerprints.setdefault(fp, []).append(f"{file_path}:{i}")

        except Exception:
            issues.append(
                Issue(
                    str(file_path),
                    i,
                    KeyInfo("invalid", None, None, "", ""),
                    "INVALID_KEY",
                    "Failed to parse SSH public key",
                    Severity.LOW,
                )
            )


def check_permissions(file_path: Path, issues: List[Issue], kind: str):
    mode = file_path.stat().st_mode
    if kind == "private":
        if (mode & 0o077) != 0o000:
            issues.append(
                Issue(
                    str(file_path),
                    0,
                    KeyInfo("", None, None, "", ""),
                    "BAD_PERMS_PRIVATE",
                    "Private key must be 0600 (user read/write only)",
                    Severity.HIGH,
                )
            )
    elif kind == "public":
        if (mode & 0o777) != 0o644:
            issues.append(
                Issue(
                    str(file_path),
                    0,
                    KeyInfo("", None, None, "", ""),
                    "BAD_PERMS_PUBLIC",
                    "Public key should be 0644",
                    Severity.LOW,
                )
            )
    elif kind == "authorized_keys":
        if (mode & 0o777) != 0o644:
            issues.append(
                Issue(
                    str(file_path),
                    0,
                    KeyInfo("", None, None, "", ""),
                    "BAD_PERMS_AUTH",
                    "authorized_keys should be 0644",
                    Severity.MEDIUM,
                )
            )