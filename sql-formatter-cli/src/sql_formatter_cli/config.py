'''Configuration loading for SQL formatter.'''

import os
import tomli
from typing import Dict, Any

DEFAULTS: Dict[str, Any] = {
    "dialect": "postgres",
    "line_length": 88,
    "indent": "  ",
    "keyword_case": "upper",
    "normalize": True,
}


def load_config(
    config_path: str | None = None, overrides: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Load config from file, env, defaults, overrides."""
    config = DEFAULTS.copy()

    # Config file
    if config_path is None:
        for candidate in ["pyproject.toml", ".sqlformatter.toml"]:
            if os.path.exists(candidate):
                config_path = candidate
                break
    if config_path and os.path.exists(config_path):
        with open(config_path, "rb") as f:
            data = tomli.load(f)
            tool_config = data.get("tool", {}).get("sql-formatter", {}) or data.get("sql-formatter", {})
            config.update(tool_config)

    # Env vars override
    for key in DEFAULTS:
        env_key = f"SQLFMT_{key.upper().replace('-', '_')}"
        if env_value := os.getenv(env_key):
            # Simple str/int/bool conversion
            if env_value.lower() == "true":
                config[key] = True
            elif env_value.lower() == "false":
                config[key] = False
            else:
                try:
                    config[key] = int(env_value)
                except ValueError:
                    config[key] = env_value

    # CLI overrides
    if overrides:
        config.update(overrides)

    return config
