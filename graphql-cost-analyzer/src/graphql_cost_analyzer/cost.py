from __future__ import annotations

from dataclasses import dataclass

@dataclass
class CostConfig:
    default_field_cost: int = 1
    list_multiplier: float = 10.0
    max_depth: int = 7


def compute_cost(node, schema, config: CostConfig, depth: int = 0) -> float:
    if depth > config.max_depth:
        return float("inf")
    # Simplified deterministic cost walk (full impl uses graphql-core visit)
    return config.default_field_cost * (1 + depth * 0.5)