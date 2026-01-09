import pytest
import tomllib
from pathlib import Path
from license_checker_cli.detectors.python_detector import get_python_deps, _parse_req_name
from license_checker_cli.detectors.node_detector import get_node_deps
from license_checker_cli.models import LicenseInfo


@pytest.fixture
def mock_metadata(mocker):
    mock_dist = mocker.Mock()
    mock_dist.metadata.get.return_value = "MIT"
    mock_dist.metadata.get_all.return_value = ["License :: OSI Approved :: MIT License"]
    mocker.patch("license_checker_cli.detectors.python_detector.importlib.metadata.distribution", return_value=mock_dist)


def test_parse_req_name():
    assert _parse_req_name("requests>=2.31.0") == "requests"
    assert _parse_req_name("[click>=8.0]") == "click"


def test_python_detector_poetry(tmp_path: Path, mock_metadata):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"
rich = "^13.7.0"
    """)
    deps = get_python_deps(tmp_path)
    assert len(deps) == 2
    assert deps[0].name == "requests"
    assert deps[0].license == "MIT"


def test_python_detector_pep621(tmp_path: Path, mock_metadata):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
dependencies = [
  "requests>=2.31.0",
  "rich<14.0",
]
    """)
    deps = get_python_deps(tmp_path)
    assert len(deps) == 2


def test_node_detector(tmp_path: Path):
    lockfile = tmp_path / "package-lock.json"
    lockfile.write_text("""
{
  "packages": {
    "": {
      "dependencies": {
        "lodash": "^4.17.21"
      }
    },
    "node_modules/lodash": {
      "version": "4.17.21",
      "license": "MIT"
    }
  }
}
    """)
    deps = get_node_deps(tmp_path)
    assert len(deps) == 1
    assert deps[0].name == "lodash"
    assert deps[0].license == "MIT"