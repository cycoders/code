import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def tmp_storage(tmp_path: Path):
    """Temp storage."""
    from pulse_cli.storage import Storage
    return Storage(str(tmp_path / "test.db"))