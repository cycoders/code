from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..models import Issue


class Rule(ABC):
    """Base class for audit rules."""

    rule_id: str = "base"
    severity: str = "warn"

    @abstractmethod
    def check(self, spec: Dict[str, Any]) -> List[Issue]:
        """Run checks and yield Issues."""
        pass
