from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class Settings:
    """Configuration for link auditing."""

    concurrency: int = 50
    timeout: float = 10.0
    max_retries: int = 3
    follow_redirects: bool = True
    ignore_patterns: List[str] = None

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = []

    def filter_link(self, url: str) -> bool:
        """Check if link should be ignored."""
        lower_url = url.lower()
        if any(
            lower_url.startswith(p) or p in lower_url
            for p in self.ignore_patterns
        ):
            return False
        if any(lower_url.startswith(prefix) for prefix in ["mailto:", "tel:", "javascript:", "data:", "#"]):
            return False
        return "http" in lower_url[:4]
