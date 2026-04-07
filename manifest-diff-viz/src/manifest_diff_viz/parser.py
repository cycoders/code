import yaml
from pathlib import Path
from typing import List, Dict, Any

IGNORED_KEYS = {'apiVersion', 'kind', 'metadata'}  # Keep for keying

 def load_manifests(paths: List[Path]) -> List[Dict[str, Any]]:
    """Load all YAML manifests from paths (files or dirs)."""
    docs: List[Dict[str, Any]] = []
    for path in paths:
        if path.is_dir():
            for yaml_file in path.rglob('*.yaml') + path.rglob('*.yml'):
                docs.extend(_load_yaml_file(yaml_file))
        else:
            docs.extend(_load_yaml_file(path))
    return [doc for doc in docs if _is_resource(doc)]

def _load_yaml_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load multi-doc YAML file."""
    try:
        with open(file_path, 'r') as f:
            return list(yaml.safe_load_all(f))
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")

def _is_resource(doc: Dict[str, Any]) -> bool:
    """Filter valid K8s resources."""
    if not isinstance(doc, dict):
        return False
    return 'kind' in doc and 'apiVersion' in doc and 'metadata' in doc

def get_resource_key(doc: Dict[str, Any]) -> str:
    """Unique key: apiVersion-kind-namespace-name."""
    md = doc.get('metadata', {})
    ns = md.get('namespace', 'default')
    name = md.get('name', 'unknown')
    return f"{doc.get('apiVersion', 'v1')}-{doc.get('kind', 'Unknown')}-{ns}-{name}"