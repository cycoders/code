from dataclasses import dataclass
from typing import Optional


@dataclass
class LicenseInfo:
    name: str
    version: str
    license: str
    classification: Optional[str] = None
    approved: bool = False
    spdx: Optional[str] = None