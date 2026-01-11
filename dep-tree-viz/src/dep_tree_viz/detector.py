from pathlib import Path
from typing import Tuple, Optional

def detect_lockfile(project_path: Path) -> Optional[Tuple[str, Path, Optional[Path]]]:
    """
    Detect supported lockfile and return (parser_type, lock_path, manifest_path).
    """
    poetry_lock = project_path / "poetry.lock"
    if poetry_lock.exists():
        pyproject = project_path / "pyproject.toml"
        return "poetry", poetry_lock, pyproject if pyproject.exists() else None

    npm_lock = project_path / "package-lock.json"
    if npm_lock.exists():
        package_json = project_path / "package.json"
        return "npm", npm_lock, package_json if package_json.exists() else None

    cargo_lock = project_path / "Cargo.lock"
    if cargo_lock.exists():
        cargo_toml = project_path / "Cargo.toml"
        return "cargo", cargo_lock, cargo_toml if cargo_toml.exists() else None

    return None