from dataclasses import dataclass
from typing import List, Callable
from pathlib import Path
from .parsers import parse_npm_lock, parse_poetry_lock, parse_cargo_lock

ParseResult = tuple[dict[str, str], Optional[int], Optional[dict[str, int]]]

@dataclass
class Ecosystem:
    name: str
    required_files: List[str]
    lockfile: str
    update_cmd: List[str]
    parse_lock: Callable[[Path], ParseResult]

npm = Ecosystem(
    name="npm",
    required_files=["package.json", "package-lock.json"],
    lockfile="package-lock.json",
    update_cmd=["npm", "update"],
    parse_lock=parse_npm_lock,
)

poetry = Ecosystem(
    name="poetry",
    required_files=["pyproject.toml", "poetry.lock"],
    lockfile="poetry.lock",
    update_cmd=["poetry", "update"],
    parse_lock=parse_poetry_lock,
)

cargo = Ecosystem(
    name="cargo",
    required_files=["Cargo.toml", "Cargo.lock"],
    lockfile="Cargo.lock",
    update_cmd=["cargo", "update"],
    parse_lock=parse_cargo_lock,
)

ecosystems = {
    "npm": npm,
    "poetry": poetry,
    "cargo": cargo,
}
