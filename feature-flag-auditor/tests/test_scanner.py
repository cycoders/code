import pytest
from pathlib import Path

from feature_flag_auditor.config import Config, Pattern
from feature_flag_auditor.scanner import scan_directory, Usage


def test_scan_python_file(sample_py_file: Path):
    config_dict = {
        "patterns": [
            {
                "name": "env",
                "regex": r'os\.getenv\s*\(\s*["\']([^"\']+)["\']',
                "langs": ["python"],
            }
        ],
        "exts": {"python": ["py"]},
    }
    config = Config.model_validate(config_dict)

    usages = scan_directory(sample_py_file.parent, config)

    assert len(usages) == 2
    assert usages[0].flag == "FF_USER_LOGIN"
    assert usages[1].flag == "FF_DARK_MODE"


def test_scan_js_file(sample_js_file: Path):
    config_dict = {
        "patterns": [
            {
                "name": "js-env",
                "regex": r'process\.env\[["\']([^"\']+)["\']\]',
                "langs": ["js"],
            }
        ],
        "exts": {"js": ["js"]},
    }
    config = Config.model_validate(config_dict)

    usages = scan_directory(sample_js_file.parent, config)
    assert len(usages) == 1
    assert usages[0].flag == "FF_FEATURE"


def test_ignore_gitignore(tmp_path: Path):
    (tmp_path / ".gitignore").write_text("test.py\n")
    sample_file = tmp_path / "test.py"
    sample_file.write_text('os.getenv("FF_X")')

    config = Config.model_validate({
        "patterns": [{"name": "env", "regex": r'os\.getenv\s*\(\s*["\']([^"\']+)["\']'}],
        "exts": {"python": ["py"]},
    })

    usages = scan_directory(tmp_path, config)
    assert len(usages) == 0  # Ignored


def test_invalid_regex(tmp_path: Path):
    config_dict = {
        "patterns": [{"name": "bad", "regex": "[", "langs": ["python"]}],
    }
    config = Config.model_validate(config_dict)
    usages = scan_directory(tmp_path, config)
    assert len(usages) == 0  # No crash
