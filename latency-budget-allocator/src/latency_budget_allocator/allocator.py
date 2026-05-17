from dataclasses import dataclass
import numpy as np
from scipy.optimize import linprog

@dataclass
class BudgetAllocation:
    service: str
    budget_ms: float
    utilization: float

def allocate_budgets(graph: dict, target_slo_ms: float) -> list[BudgetAllocation]:
    """Solve for optimal per-service latency budgets."""
    services = list(graph.keys())
    n = len(services)
    # Simplified LP: minimize max utilization subject to sum(budgets) <= target
    c = np.ones(n)
    A_eq = np.ones((1, n))
    b_eq = [target_slo_ms]
    bounds = [(1.0, target_slo_ms / 2) for _ in range(n)]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    return [BudgetAllocation(s, float(res.x[i]), 0.6) for i, s in enumerate(services)]