from pathlib import Path
import yaml

DEFAULT_RULES = {"auth_before_cors": True, "rate_limit_first": True}

def load_config(path: str | None):
    if path:
        return yaml.safe_load(Path(path).read_text())
    return DEFAULT_RULES