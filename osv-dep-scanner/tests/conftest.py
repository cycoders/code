import json
import pathlib
from typing import Iterator

import pytest
from typer.testing import CliRunner

from osv_dep_scanner.cli import app

runner = CliRunner()


@pytest.fixture
def sample_package_lock() -> str:
    return '''{
  "name": "test",
  "lockfileVersion": 3,
  "packages": {
    "": {"name": "test", "version": "1.0.0"},
    "node_modules/lodash": {"version": "4.17.21"}
  }
}'''


@pytest.fixture
def sample_poetry_lock() -> str:
    return '''{
  "package": [
    {"name": "requests", "version": "2.32.4"},
    {"name": "urllib3", "version": "1.26.5"}
  ]
}'''


@pytest.fixture
def sample_cargo_lock() -> str:
    return '''
[[package]]
name = "serde"
version = "1.0.210"

[[package]]
name = "tokio"
version = "1.40.0"
'''
