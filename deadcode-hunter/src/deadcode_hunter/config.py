from dataclasses import dataclass, field
from pathlib import Path
import tomllib
from typing import List


@dataclass
class Config:
    """Configuration for deadcode-hunter."""

    ignores: List[str] = field(
        default_factory=lambda: [
            ".git",
            "venv",
            ".venv",
            "env",
            "__pycache__",
            "*.egg-info",
            "build",
            "dist",
            "node_modules",
            "tests",
            "test",
            "examples",
        ]
    )
    min_confidence: int = 50


def load_config(config_file: str | None = None) -> Config:
    """Load config from .deadcodehunter.toml or pyproject.toml[tool.deadcode-hunter]."""

    cfg = Config()

    # Custom config file
    if config_file and Path(config_file).exists():
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        _merge_tool_config(data, cfg)

    # pyproject.toml fallback
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        _merge_tool_config(data, cfg)

    return cfg


def _merge_tool_config(data: dict, cfg: Config) -> None:
    tool_sec = data.get("tool", {}).get("deadcode-hunter", {})
    if isinstance(tool_sec.get("ignores"), list):
        cfg.ignores.extend(tool_sec["ignores"])
    if isinstance(tool_sec.get("min_confidence"), int):
        cfg.min_confidence = tool_sec["min_confidence"]
