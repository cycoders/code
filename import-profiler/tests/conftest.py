import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory


@pytest.fixture
def tmp_script():
    """Yield path to temp script; write content via call.

    Usage: def test(tmp_script): path = tmp_script('import os')
    """
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.py"
        yield lambda content: (path.write_text(content), str(path))[1]
