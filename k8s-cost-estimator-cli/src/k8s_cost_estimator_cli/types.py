from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Resources:
    cpu_cores: float
    mem_gib: float


@dataclass
class Config:
    provider: str
    region: str
    nodes: int
    utilization: float
    days: int


@dataclass
class CostBreakdown:
    namespace: str
    kind: str
    name: str
    replicas: int
    cpu_cores: float
    mem_gib: float
    total_cost: float

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)
