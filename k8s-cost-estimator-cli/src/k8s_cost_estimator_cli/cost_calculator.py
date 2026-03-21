from .pricing_data import get_prices
from .resource_analyzer import extract_resources
from .types import Config, CostBreakdown, Resources


def calculate_costs(obj: dict, cfg: Config) -> CostBreakdown:
    ns = obj["metadata"].get("namespace", "default")
    name = obj["metadata"]["name"]
    kind = obj["kind"]

    resources = extract_resources(obj, cfg.nodes)

    prices = get_prices(cfg.provider, cfg.region)
    cpu_cost = resources.cpu_cores * prices.cpu_per_core_hour * 24 * cfg.days * cfg.utilization
    mem_cost = resources.mem_gib * prices.mem_per_gib_hour * 24 * cfg.days * cfg.utilization
    total = cpu_cost + mem_cost

    return CostBreakdown(
        namespace=ns,
        kind=kind,
        name=name,
        replicas=resources.replicas if hasattr(resources, 'replicas') else 1,  # Approx
        cpu_cores=round(resources.cpu_cores, 2),
        mem_gib=round(resources.mem_gib, 2),
        total_cost=round(total, 2),
    )
