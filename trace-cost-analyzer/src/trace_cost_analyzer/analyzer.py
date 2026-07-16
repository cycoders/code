import orjson
from pathlib import Path
from typing import Any

def analyze_traces(path: str, vendor: str, config_path: str | None) -> dict[str, Any]:
    spans = 0
    for line in Path(path).read_bytes().splitlines():
        if line.strip():
            spans += 1
    # placeholder realistic pricing model
    cost_per_million = {'datadog': 1.70, 'honeycomb': 0.95}.get(vendor, 1.5)
    monthly_cost = (spans / 1_000_000) * cost_per_million * 30 * 24
    return {'spans': spans, 'estimated_monthly_usd': round(monthly_cost, 2)}