import json
import pytest
from pytest_mock import MockerFixture
from subprocess import CompletedProcess

from sbom_generator_cli.detectors.python_detector import PythonDetector

from sbom_generator_cli.models import Component


@pytest.mark.parametrize("detector", [PythonDetector()])
def test_detect(detector: 'Detector', tmp_path):
    (tmp_path / "pyproject.toml").touch()
    assert detector.detect(tmp_path)


def test_poetry_parse(mocker: MockerFixture):
    mock_result = CompletedProcess(
        returncode=0,
        stdout=json.dumps([{"name": "requests", "version": "2.31.0"}]),
    )
    mocker.patch("subprocess.run", return_value=mock_result)

    detector = PythonDetector()
    # Assume cwd has poetry.lock
    comps = detector._parse_poetry(Path("."))
    assert len(comps) == 1
    assert comps[0].name == "requests"
    assert comps[0].purl == "pkg:pypi/requests@2.31.0"


def test_pip_parse(mocker: MockerFixture):
    mock_result = CompletedProcess(
        returncode=0,
        stdout=json.dumps([{"name": "pydantic", "version": "2.8.2"}]),
    )
    mocker.patch("subprocess.run", return_value=mock_result)

    detector = PythonDetector()
    comps = detector._parse_pip(Path("."))
    assert len(comps) == 1
    assert comps[0].purl == "pkg:pypi/pydantic@2.8.2"


# Similar tests for other detectors


def test_cargo_parse(mocker: MockerFixture):
    from sbom_generator_cli.detectors.cargo_detector import CargoDetector

    data = {
        "packages": [
            {
                "name": "tokio",
                "version": "1.36.0",
                "id": "tokio 1.36.0 (registry+https://github.com/rust-lang/crates.io-index)",
            }
        ]
    }
    mock_result = CompletedProcess(returncode=0, stdout=json.dumps(data))
    mocker.patch("subprocess.run", return_value=mock_result)

    detector = CargoDetector()
    comps = detector.collect(Path("."))
    assert len(comps) == 1
    assert comps[0].name == "tokio"


# Edge cases

def test_error_handling(mocker: MockerFixture):
    mocker.patch("subprocess.run", return_value=CompletedProcess(returncode=1, stdout=""))
    detector = PythonDetector()
    with pytest.raises(RuntimeError):
        detector._parse_poetry(Path("."))
