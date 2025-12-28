from pathlib import Path
from typing import List, Optional

import tomllib
import yaml
from pydantic import BaseModel, Field, validator


def load_config(git_root: Path) -> "LintConfig":
    """
    Load config from pyproject.toml or .conventional-commit-lintrc.yaml in git_root.

    Priority: pyproject.toml > YAML.
    """
    config_data: dict = {}

    # pyproject.toml
    pyproject_path = git_root / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        tool_cfg = data.get("tool", {}).get("conventional-commit-linter", {})
        config_data.update(tool_cfg)

    # .conventional-commit-lintrc.yaml (overrides)
    yaml_path = git_root / ".conventional-commit-lintrc.yaml"
    if yaml_path.exists():
        with open(yaml_path) as f:
            yaml_data = yaml.safe_load(f) or {}
            config_data.update(yaml_data)

    return LintConfig(**config_data)


class LintConfig(BaseModel):
    types: List[str] = Field(
        default_factory=lambda: [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "build",
            "ci",
            "chore",
            "revert",
        ]
    )
    scopes: Optional[List[str]] = None
    max_subject_length: int = 50
    max_line_length: int = 72

    @validator("types", pre=True)
    def lowercase_types(cls, v):
        return [t.lower() for t in v]
