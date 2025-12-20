import yaml
from pathlib import Path
from typing import List, Dict, Any

def load_cassette(cassette_path: str) -> List[Dict[str, Any]]:
    """Load interactions from YAML cassette."""
    path = Path(cassette_path)
    if not path.exists():
        return []
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or []
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error loading cassette {cassette_path}: {e}")
        return []

def append_to_cassette(cassette_path: str, interaction: Dict[str, Any]) -> None:
    """Append interaction to cassette."""
    interactions = load_cassette(cassette_path)
    interactions.append(interaction)
    path = Path(cassette_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(interactions, f, default_flow_style=False, sort_keys=False, allow_unicode=True)