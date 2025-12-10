import yaml
from pathlib import Path
from typing import Dict, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    "type_to_section": {
        "feat": "Added",
        "fix": "Fixed",
        "docs": "Documentation",
        "style": "Styling",
        "refactor": "Refactoring",
        "perf": "Performance",
        "test": "Tests",
        "build": "Build system",
        "ci": "Continuous Integration",
        "chore": "Miscellaneous Chores",
        "revert": "Reverts",
    },
    "section_order": [
        "Added",
        "Fixed",
        "Documentation",
        "Styling",
        "Refactoring",
        "Performance",
        "Tests",
        "Build system",
        "Continuous Integration",
        "Miscellaneous Chores",
        "Reverts",
    ],
}


def load_config(config_path: Path | None) -> Dict[str, Any]:
    """Load config from YAML or return defaults."""
    if config_path and config_path.exists():
        with open(config_path, encoding="utf-8") as file:
            user_config = yaml.safe_load(file) or {}
        config = DEFAULT_CONFIG.copy()
        config.update(user_config)
        return config
    return DEFAULT_CONFIG