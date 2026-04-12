'''Tests for normalizer.''' 

import pytest
from semantic_diff_cli.normalizer import normalize_content, PRETTIER_PARSERS
from pathlib import Path


class TestNormalize:
    def test_python_black(self, mocker):
        from black import format_file_contents
        mock_format = mocker.patch("black.format_file_contents")
        mock_format.return_value = ("formatted\ncode", None)

        result = normalize_content("test.py", "raw code")
        assert result == "formatted\ncode"
        mock_format.assert_called_once()

    def test_go_gofmt(self, mocker):
        mock_subp = mocker.patch("subprocess.run")
        mock_subp.return_value = subprocess.CompletedProcess([], 0, stdout="fmt go")

        result = normalize_content("test.go", "raw")
        assert result == "fmt go"

    def test_rust_rustfmt(self, mocker):
        mock_subp = mocker.patch("subprocess.run")
        mock_subp.return_value = subprocess.CompletedProcess([], 0, stdout="fmt rs")

        result = normalize_content("test.rs", "raw")
        assert result == "fmt rs"

    @pytest.mark.parametrize("ext,parser", PRETTIER_PARSERS.items())
    def test_prettier(self, ext, mocker):
        mock_subp = mocker.patch("subprocess.run")
        mock_subp.return_value = subprocess.CompletedProcess([], 0, stdout="pretty")

        fp = f"test{ext}"
        result = normalize_content(fp, "raw")
        assert result == "pretty"
        mock_subp.assert_called_once()

    def test_fallback(self, mocker, capsys):
        mocker.patch("subprocess.run", side_effect=FileNotFoundError)
        result = normalize_content("test.txt", "raw")
        assert result == "raw"
        assert "failed" in capsys.readouterr().err

    def test_unknown_ext(self):
        result = normalize_content("test.bin", "raw")
        assert result == "raw"
