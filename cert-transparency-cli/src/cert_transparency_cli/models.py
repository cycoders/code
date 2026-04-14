from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional

@dataclass
class CertificateEntry:
    id: int
    logged_at: datetime
    not_before: datetime
    not_after: datetime
    issuer_name: str
    common_name: str
    cert_link: str
    serial_number: str = ""
    subject_alt_names: List[str] = field(default_factory=list)
    signature_algorithm: Optional[str] = None
    public_key_algorithm: Optional[str] = None