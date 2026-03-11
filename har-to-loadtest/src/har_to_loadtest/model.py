from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class HttpRequest:
    """Normalized HTTP request from HAR entry."""

    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str]
    json_body: Optional[Dict[str, Any]]
