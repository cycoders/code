import pytest
from pathlib import Path
from upgrade_dryrun.ecosystems import ecosystems, Ecosystem


def test_ecosystems_defined():
    assert len(ecosystems) == 3
    assert all(isinstance(eco, Ecosystem) for eco in ecosystems.values())


def test_npm_required_files(tmp_path: Path):
    npm = ecosystems["npm"]
    assert npm.required_files == ["package.json", "package-lock.json"]
    assert npm.update_cmd == ["npm", "update"]
