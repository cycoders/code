import yaml
from pathlib import Path
from typing import Iterator, Dict, Any

SUPPORTED_KINDS = {"Deployment", "StatefulSet", "DaemonSet"}
K8S_VERSION_FIELDS = {"apiVersion", "kind", "metadata"}


def scan_manifests(root: Path) -> Iterator[Dict[str, Any]]:
    """Scan directory recursively for valid K8s YAML manifests."""
    for yaml_file in root.rglob("*.yaml"):
        if yaml_file.is_file() and not yaml_file.name.startswith("."):
            try:
                data = yaml.safe_load(yaml_file.read_text())
                if isinstance(data, dict) and _is_supported_k8s_object(data):
                    yield data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and _is_supported_k8s_object(item):
                            yield item
            except yaml.YAMLError:
                continue  # Skip invalid YAML


def _is_supported_k8s_object(obj: Dict[str, Any]) -> bool:
    return (
        set(obj.keys()) & K8S_VERSION_FIELDS == K8S_VERSION_FIELDS
        and obj["kind"] in SUPPORTED_KINDS
    )
