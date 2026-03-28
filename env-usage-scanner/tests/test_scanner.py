import pytest
from pathlib import Path
from collections import defaultdict

import env_usage_scanner.scanner as scanner
import env_usage_scanner.models as models


def test_scan_directory(temp_dir: Path):
    (temp_dir / "app.py").write_text("os.getenv('TEST_VAR')")
    (temp_dir / "Dockerfile").write_text("ENV TEST_ARG=val")

    usages = scanner.scan_directory(temp_dir)
    assert len(usages) == 2
    assert "TEST_VAR" in usages
    assert "TEST_ARG" in usages


def test_exclude_paths(temp_dir: Path):
    (temp_dir / "venv" / "script.py").write_text("os.getenv('SKIP')")
    usages = scanner.scan_directory(temp_dir)
    assert not usages  # Excluded by default


def test_parse_env_file(temp_dir: Path):
    env_file = temp_dir / ".env"
    env_file.write_text("DB_URL=postgres://\nUNUSED_VAR=foo\n# comment")
    defined = scanner.parse_env_file(env_file)
    assert defined == {"DB_URL", "UNUSED_VAR"}
