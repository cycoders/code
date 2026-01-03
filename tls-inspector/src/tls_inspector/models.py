from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Certificate:
    subject: str
    issuer: str
    serial: str
    not_before: str
    not_after: str
    san: List[str]
    key_type: str
    key_size: int
    sig_algo: str
    version: str


@dataclass
class TLSReport:
    host: str
    port: int
    protocols: List[str]
    negotiated_protocol: str
    negotiated_cipher: str
    supported_ciphers: List[str]
    cert_chain: List[Certificate]
    chain_valid: bool
    hsts: Optional[Dict[str, Any]]
    security_grade: str