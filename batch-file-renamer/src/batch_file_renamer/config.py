import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_rules(config_path: Optional[str]) -> List[Dict[str, Any]]:
    """Load rules from YAML config file."""
    if not config_path:
        return []
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_file) as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])