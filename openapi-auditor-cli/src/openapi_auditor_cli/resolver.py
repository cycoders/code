import copy
from typing import Any, Dict, Set

import yaml
from pathlib import Path


def load_spec(spec_path: Path) -> Dict[str, Any]:
    """Load OpenAPI spec from YAML/JSON file."""
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def resolve_ref(root_spec: Dict[str, Any], ref: str, visited: Set[str] = None) -> Any:
    """Resolve internal $ref pointer."""
    if visited is None:
        visited = set()
    if ref in visited:
        raise ValueError(f"Cycle detected in ref: {ref}")
    visited.add(ref)
    if not ref.startswith('#/'):
        raise ValueError(f"External refs not supported: {ref}")
    parts = ref[2:].split('/')
    current = root_spec
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                current = None
        if current is None:
            raise ValueError(f"Broken ref '{ref}' at part '{part}'")
    return current


def deref_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively dereference all $refs, returning a fully resolved spec."""
    def _deref(obj: Any, root: Dict[str, Any], visited: Set[str]) -> Any:
        if isinstance(obj, dict):
            if '$ref' in obj:
                ref = obj['$ref']
                try:
                    return resolve_ref(root, ref, visited)
                except ValueError as e:
                    # Replace broken ref with error marker
                    return {'$ref_error': str(e)}
            return {k: _deref(v, root, visited.copy()) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_deref(item, root, visited.copy()) for item in obj]
        return obj

    return _deref(spec, spec, set())
