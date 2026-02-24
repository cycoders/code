import json
from typing import Dict, Any, List
from rich.panel import Panel
from rich.text import Text

def safe_json_load(text: str) -> Any:
    """Safely load JSON, return None on error."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def calculate_stats(endpoints: Dict, total_entries: int) -> Panel:
    num_endpoints = sum(len(ops) for ops in endpoints.values())
    text = Text()
    text.append(f"Processed {total_entries} entries → ")
    text.append(f"{num_endpoints} endpoints", style="bold green")
    return Panel(text, title="Stats", border_style="green")
