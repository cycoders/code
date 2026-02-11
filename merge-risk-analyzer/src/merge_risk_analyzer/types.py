from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FileRisk:
    """Represents risk assessment for a single file."""

    path: str
    overlap_ratio: float
    change_size: int
    historical_conflicts: int
    risk_score: float
    risk_level: str  # low|medium|high
    suggestion: str