from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CertificateInfo:
    subject: str
    issuer: str
    not_valid_before: datetime
    not_valid_after: datetime
    serial_number: str
    key_algorithm: str
    key_size: Optional[int]
    subject_alt_names: List[str]
    sha256_fingerprint: str
    version: str


@dataclass
class PrivateKeyInfo:
    algorithm: str
    bit_size: int
    sha256_fingerprint: str
    public_modulus: Optional[str]  # RSA


@dataclass
class CsrInfo:
    subject: str
    public_key_algorithm: str
    public_key_size: int
    sha256_fingerprint: str


PemParseResult = dict[str, CertificateInfo | PrivateKeyInfo | CsrInfo | str]