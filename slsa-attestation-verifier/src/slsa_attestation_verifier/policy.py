from pathlib import Path
import yaml
from typing import Any

def load_policy(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return yaml.safe_load(Path(path).read_text()) or {}

def evaluate(attestation: dict, artifact: str, policy: dict) -> Any:
    # Placeholder policy evaluation
    return type('R', (), {'valid': True, 'reason': ''})()
