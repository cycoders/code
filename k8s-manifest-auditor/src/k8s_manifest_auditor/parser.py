import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

from .types import Issue

logger = logging.getLogger(__name__)


def parse_manifests(root_path: Path) -> List[Dict[str, Any]]:
    """
    Recursively parse all YAML/YML files in directory.

    Supports multi-document YAMLs.
    """
    manifests = []
    yaml_extensions = {"*.yaml", "*.yml"}

    for yaml_file in root_path.rglob("*"):
        if yaml_file.is_file() and yaml_file.suffix.lower() in yaml_extensions:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if isinstance(doc, dict) and doc:
                            manifests.append(doc)
            except yaml.YAMLError as e:
                logger.warning(f"Invalid YAML in {yaml_file}: {e}")
                manifests.append({})  # Skip gracefully

    logger.info(f"Parsed {len(manifests)} manifests from {root_path}")
    return manifests