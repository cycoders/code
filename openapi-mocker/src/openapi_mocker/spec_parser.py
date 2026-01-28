import json
import logging
from pathlib import Path
from typing import Dict, Any

import yaml

from .types import OpenAPISpec


logger = logging.getLogger(__name__)


def load_spec(spec_path: Path) -> OpenAPISpec:
    """
    Load and validate OpenAPI 3.0 spec from YAML or JSON file.

    Raises:
        ValueError: Invalid spec version or file not found.
    """
    if not spec_path.exists():
        raise ValueError(f"Spec file not found: {spec_path}")

    try:
        if spec_path.suffix == '.json':
            with spec_path.open('r') as f:
                data: Dict[str, Any] = json.load(f)
        else:
            with spec_path.open('r') as f:
                data: Dict[str, Any] = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse spec: {e}") from e

    if not isinstance(data, dict) or not data.get('openapi', '').startswith('3.0.'):
        raise ValueError("Only OpenAPI 3.0 specs are supported.")

    spec = OpenAPISpec(**data)
    logger.info(f"Loaded spec: {spec.info.get('title', 'Untitled')} with {len(spec.paths)} paths")
    return spec