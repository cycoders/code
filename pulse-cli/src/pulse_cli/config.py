import yaml
from pathlib import Path
from typing import Optional

from .models import PulseConfig

CONFIG_DIR = Path.home() / ".pulse-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

SAMPLE_CONFIG = """
endpoints:
  - name: httpbin
    url: https://httpbin.org/json
    expected_status: [200]
    max_resp_time: 500.0
    content_match: 'slideshow'
    check_cert: true
"""

def init_config() -> None:
    """Initialize default config if missing."""
    CONFIG_DIR.mkdir(exist_ok=True)
    if CONFIG_PATH.exists():
        print(f"Config exists: {CONFIG_PATH}")
        return
    with open(CONFIG_PATH, "w") as f:
        f.write(SAMPLE_CONFIG)
    print(f"Initialized: {CONFIG_PATH}")

def load_config(path: Optional[Path] = None) -> PulseConfig:
    """Load YAML config to Pydantic model."""
    path = path or CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"No config at {path}. Run 'pulse-cli init'.")
    with open(path) as f:
        data = yaml.safe_load(f)
    return PulseConfig.model_validate(data)

def save_config(config: PulseConfig, path: Optional[Path] = None) -> None:
    """Save Pydantic config to YAML."""
    path = path or CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {path}")