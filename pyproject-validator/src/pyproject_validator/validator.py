from __future__ import annotations

import tomli
from typing import Any

from .rules import RULES


def validate(toml_path: str) -> list[str]:
    with open(toml_path, "rb") as f:
        data: dict[str, Any] = tomli.load(f)
    errors: list[str] = []
    for rule in RULES:
        errors.extend(rule(data))
    return errors