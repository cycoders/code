from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Job:
    """Represents a single job in a GitHub Actions workflow."""

    name: str
    needs: List[str]
    steps: List[dict[str, Any]]
    strategy: Optional[dict[str, Any]] = None