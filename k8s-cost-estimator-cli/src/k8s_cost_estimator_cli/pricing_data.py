from dataclasses import dataclass
from typing import Dict

@dataclass
class Pricing:
    cpu_per_core_hour: float
    mem_per_gib_hour: float

PRICING: Dict[str, Dict[str, Pricing]] = {
    "aws": {
        "us-east-1": Pricing(cpu_per_core_hour=0.02496, mem_per_gib_hour=0.00298),
        "us-west-2": Pricing(cpu_per_core_hour=0.02592, mem_per_gib_hour=0.00310),
    },
    "gcp": {
        "us-central1": Pricing(cpu_per_core_hour=0.01992, mem_per_gib_hour=0.00226),
        "europe-west1": Pricing(cpu_per_core_hour=0.02291, mem_per_gib_hour=0.00260),
    },
    "azure": {
        "eastus": Pricing(cpu_per_core_hour=0.0224, mem_per_gib_hour=0.0027),
        "westus2": Pricing(cpu_per_core_hour=0.0224, mem_per_gib_hour=0.0027),
    },
}


def get_prices(provider: str, region: str) -> Pricing:
    prices = PRICING.get(provider, {}).get(region, Pricing(0.02, 0.0025))
    if prices.cpu_per_core_hour == 0:
        raise ValueError(f"Pricing not found for {provider}/{region}")
    return prices
