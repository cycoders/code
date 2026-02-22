from pathlib import Path
from typing import Dict
import json
import shlex
from dotenv import dotenv_values


def load_env(path: Path) -> Dict[str, str]:
    """Load .env file into dict."""
    if not path.is_file():
        raise FileNotFoundError(f"Env file not found: {path}")
    return dotenv_values(str(path))


def dump_env(expanded: Dict[str, str], output: Path, json_output: bool = False) -> None:
    """Dump expanded dict to .env or JSON file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if json_output:
        with output.open('w') as f:
            json.dump(expanded, f, indent=2)
    else:
        with output.open('w') as f:
            for key in sorted(expanded):
                f.write(f"{key}={shlex.quote(expanded[key])}\n")