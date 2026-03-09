import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # NPM sample
    npm_dir = data_dir / "npm"
    npm_dir.mkdir()
    npm_lock = npm_dir / "package-lock.json"
    npm_lock.write_text(json.dumps({
        "lockfileVersion": 3,
        "packages": {
            "": {},
            "node_modules/lodash": {
                "name": "lodash",
                "version": "4.17.21",
                "unpackedSize": 1401024
            },
            "node_modules/express": {
                "name": "express",
                "version": "4.18.2",
                "unpackedSize": 512000
            }
        }
    }), encoding="utf-8")
    (npm_dir / "package.json").touch()

    # Poetry sample
    poetry_dir = data_dir / "poetry"
    poetry_dir.mkdir()
    poetry_lock = poetry_dir / "poetry.lock"
    poetry_lock.write_text("""
[[package]]
name = "requests"
version = "2.31.0"

[[package]]
name = "certifi"
version = "2023.7.22"
""")
    (poetry_dir / "pyproject.toml").touch()

    # Cargo sample
    cargo_dir = data_dir / "cargo"
    cargo_dir.mkdir()
    cargo_lock = cargo_dir / "Cargo.lock"
    cargo_lock.write_text("""
[[package]]
name = "serde"
version = "1.0.193"

[[package]]
name = "tokio"
version = "1.35.1"
""")
    (cargo_dir / "Cargo.toml").touch()

    return data_dir
