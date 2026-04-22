import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from arch_boundary_auditor.analyzer import analyze, get_package_prefix
from arch_boundary_auditor.config import Config, Layer


@pytest.fixture
def sample_config():
    return Config(
        layers=[
            Layer(name="domain", package_prefixes=["domain."], allowed_layers=["utils"], forbidden_layers=["infra"]),
            Layer(name="infra", package_prefixes=["infra."], allowed_layers=["domain"]),
            Layer(name="utils", package_prefixes=["utils."]),
        ],
        src_dir="src",
        allow_third_party=True,
    )


def test_get_package_prefix():
    root = Path("/proj")
    f = root / "src/domain/user.py"
    assert get_package_prefix(root, "src", f) == "domain."

    f2 = root / "domain/standalone.py"  # no src
    assert get_package_prefix(root, "src", f2) == "domain."


def test_analyze_violation(tmp_path: Path, sample_config):
    root = tmp_path
    (root / "src/domain").mkdir(parents=True)
    (root / "src/infra").mkdir(parents=True)

    # Violation: domain imports infra
    (root / "src/domain/user.py").write_text("from infra.db import X\n")
    # OK: infra imports domain
    (root / "src/infra/db.py").write_text("import domain\n")

    violations = analyze(root, sample_config)
    assert len(violations) == 1
    v = violations[0]
    assert v.from_layer == "domain"
    assert v.to_layer == "infra"
    assert v.severity == "error"


def test_no_violations(tmp_path: Path, sample_config):
    root = tmp_path
    (root / "src/domain").mkdir(parents=True)
    (root / "src/domain/service.py").write_text("from utils import helper\nimport requests\n")
    violations = analyze(root, sample_config)
    assert len(violations) == 0


def test_ignore_glob(tmp_path: Path, sample_config):
    sample_config.ignore_globs = ["**/tests/**"]
    root = tmp_path
    (root / "src/domain/tests/bad.py").write_text("import infra")
    violations = analyze(root, sample_config)
    assert len(violations) == 0  # ignored