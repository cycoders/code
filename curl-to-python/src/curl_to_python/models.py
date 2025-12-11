from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class CurlParsed:
    """Parsed representation of a curl command."""

    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    data: str = ""
    json_data: Dict[str, Any] = field(default_factory=dict)
    form_data: Dict[str, str] = field(default_factory=dict)
    files: Dict[str, str] = field(default_factory=dict)  # field -> filename
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    is_get: bool = False
