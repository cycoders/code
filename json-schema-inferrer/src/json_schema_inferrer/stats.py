from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValueStats:
    type_counts: Counter[str] = field(default_factory=Counter)
    string_values: Counter[str] = field(default_factory=Counter)
    number_values: List[float] = field(default_factory=list)
    integer_count: int = 0
    bool_true_count: int = 0
    bool_false_count: int = 0

    def update(self, value: Any) -> None:
        if value is None:
            self.type_counts["null"] += 1
            return
        if isinstance(value, bool):
            self.type_counts["boolean"] += 1
            if value:
                self.bool_true_count += 1
            else:
                self.bool_false_count += 1
            return
        if isinstance(value, int):
            self.type_counts["integer"] += 1
            self.number_values.append(float(value))
            self.integer_count += 1
            return
        if isinstance(value, float):
            self.type_counts["number"] += 1
            self.number_values.append(value)
            return
        if isinstance(value, str):
            self.type_counts["string"] += 1
            self.string_values[value] += 1
            return
        self.type_counts["unknown"] += 1


@dataclass
class NodeStats:
    sample_count: int = 0
    structural_type: Counter[str] = field(default_factory=Counter)
    properties: Dict[str, "NodeStats"] = field(default_factory=dict)
    items_stats: Optional["NodeStats"] = None
    value_stats: Optional[ValueStats] = None

    def update(self, value: Any) -> None:
        self.sample_count += 1
        if isinstance(value, dict):
            self.structural_type["object"] += 1
            for key, v in value.items():
                if key not in self.properties:
                    self.properties[key] = NodeStats()
                self.properties[key].update(v)
        elif isinstance(value, list):
            self.structural_type["array"] += 1
            if self.items_stats is None:
                self.items_stats = NodeStats()
            for item in value:
                self.items_stats.update(item)
        else:
            self.structural_type["primitive"] += 1
            if self.value_stats is None:
                self.value_stats = ValueStats()
            self.value_stats.update(value)
