from collections import defaultdict
from typing import Any, Callable, Dict, Set

class TypeAggregator:
    def __init__(self):
        self.observations: Dict[str, Set[type]] = defaultdict(set)

    def observe(self, func: Callable, locals_: Dict[str, Any]):
        key = f"{func.__module__}.{func.__qualname__}"
        for name, value in locals_.items():
            if value is not None:
                self.observations[f"{key}:{name}"].add(type(value))

    def reduce(self) -> Dict[str, str]:
        result = {}
        for k, typeset in self.observations.items():
            if len(typeset) == 1:
                t = next(iter(typeset))
                result[k] = t.__name__
            else:
                result[k] = " | ".join(sorted(t.__name__ for t in typeset))
        return result