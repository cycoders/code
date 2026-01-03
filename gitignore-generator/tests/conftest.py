import pytest
from pathlib import Path
from gitignore_generator.detector import detect_languages, detect_frameworks


@pytest.fixture
def sample_python_project(tmp_path: Path):
    """Django + Python sample."""
    (tmp_path / "manage.py").touch()
    (tmp_path / "app.py").touch()
    (tmp_path / "utils.py").touch()
    return tmp_path


@pytest.fixture
def sample_js_project(tmp_path: Path):
    """React + Next.js sample."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies":{"next":"14","react":"18"}}')
    (tmp_path / "pages/index.js").touch()
    (tmp_path / "components.tsx").touch()
    return tmp_path