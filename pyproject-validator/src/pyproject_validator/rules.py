from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

Rule = Callable[[dict[str, Any]], list[str]]


def rule_pep621_required(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    proj = data.get("project", {})
    for field in ("name", "version"):
        if field not in proj:
            errors.append(f"Missing required PEP 621 field: project.{field}")
    return errors


def rule_build_backend(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    build = data.get("build-system", {})
    if "build-backend" not in build:
        errors.append("build-system.build-backend is required")
    return errors


RULES: list[Rule] = [rule_pep621_required, rule_build_backend]