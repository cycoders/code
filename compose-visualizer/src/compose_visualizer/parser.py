import yaml

from pathlib import Path

from typing import Dict

from .models import Compose, Service


def parse_compose(file_path: Path) -> Compose:
    """Parse Docker Compose YAML into validated model."""

    if not file_path.exists():
        raise FileNotFoundError(f"Compose file not found: {file_path}")

    with file_path.open("r") as f:
        data = yaml.safe_load(f) or {}

    services: Dict[str, Service] = {}
    svc_raw = data.get("services", {})
    for name, svc_data in svc_raw.items():
        svc = Service.model_validate(svc_data)
        svc.name = name
        services[name] = svc

    compose_data = {
        "services": services,
        **{k: v for k, v in data.items() if k not in ("services", "x-" + "*")},
    }

    return Compose.model_validate(compose_data)