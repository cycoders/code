import pytest
from pathlib import Path
from gitignore_generator.detector import detect_languages, detect_frameworks


class TestDetector:
    def test_detect_languages_python(self, sample_python_project):
        langs = detect_languages(sample_python_project)
        assert langs["python"] == 3

    def test_detect_languages_js_ts(self, sample_js_project):
        langs = detect_languages(sample_js_project)
        assert langs["json"] == 1
        assert langs["javascript"] == 1
        assert langs["typescript"] == 1

    def test_detect_languages_empty(self, tmp_path):
        langs = detect_languages(tmp_path)
        assert langs == {}

    def test_detect_frameworks_django(self, sample_python_project):
        fws = detect_frameworks(sample_python_project)
        assert "django" in fws

    def test_detect_frameworks_react_next(self, sample_js_project):
        fws = detect_frameworks(sample_js_project)
        assert "react" in fws
        assert "nextjs" in fws

    def test_detect_frameworks_flutter(self, tmp_path):
        (tmp_path / "pubspec.yaml").touch()
        fws = detect_frameworks(tmp_path)
        assert "flutter" in fws

    def test_pyproject_toml_fastapi(self, tmp_path, mocker):
        toml_content = '{"tool":{"poetry":{"dependencies":{"fastapi":"0.100"}}}}'
        (tmp_path / "pyproject.toml").write_text(toml_content)
        fws = detect_frameworks(tmp_path)
        assert "fastapi" in fws