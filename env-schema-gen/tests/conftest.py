import os
import sys
from pathlib import Path

pytest_plugins = []


@pytest.fixture(autouse=True)
def isolate_paths(monkeypatch: pytest.MonkeyPatch):
    """Prevent modules cached between test runs."""
    monkeypatch.syspath_prepend(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Sample project with various env patterns."""
    src_dir = tmp_path / 'src'
    src_dir.mkdir()

    # app.py
    (src_dir / 'app.py').write_text("""
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')  # str default
API_KEY = os.environ['API_KEY']              # required
PORT: int = int(os.getenv('PORT', '8000'))  # int inferred
    """)

    # utils.py
    (src_dir / 'utils.py').write_text("""
import os

DEBUG = os.environ.get('DEBUG', False)  # bool
FLOAT_VAL = float(os.getenv('FLOAT_VAL', '3.14'))  # float
    """)

    # Nested in lambda
    (src_dir / 'config.py').write_text("""
from pydantic import Field

def get_active():
    return os.getenv('USER_ACTIVE', 'true').lower() == 'true'
    """)

    (tmp_path / '.gitignore').write_text('venv/\n.git/\n')

    return tmp_path