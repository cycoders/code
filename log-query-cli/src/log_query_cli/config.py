import yaml
from pathlib import Path
from typing import List, Optional


def load_patterns(config_path: Optional[Path]) -> List[str]:
    """Load custom regex patterns from YAML config."""
    if not config_path or not config_path.exists():
        return []
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("patterns", [])
    except Exception as e:
        raise ValueError(f"Invalid config {config_path}: {e}")