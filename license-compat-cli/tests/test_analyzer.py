import pytest
from license_compat_cli.analyzer import analyze_project

def test_no_lockfile(tmp_path):
    with pytest.raises(SystemExit):
        analyze_project(tmp_path)