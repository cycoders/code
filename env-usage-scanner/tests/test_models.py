from pathlib import Path

import pytest
import env_usage_scanner.models as models


@pytest.mark.parametrize("usage", [
    models.Usage(Path("src/app.py"), 42, "DB_URL", "os.getenv('DB_URL')", "python"),
])
def test_usage_frozen(usage: models.Usage):
    assert hash(usage) == hash(usage)
