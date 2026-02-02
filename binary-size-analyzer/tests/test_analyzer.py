import pytest
from unittest.mock import patch

from binary_size_analyzer.analyzer import analyze_binary


class TestAnalyzeBinary:
    @pytest.mark.parametrize(
        "path, expected_format",
        [("fake.elf", "ELF"), ("fake.exe", "PE")],
    )
    def test_valid_binary(self, mock_binary, path, expected_format):
        with patch("lief.parse", return_value=mock_binary):
            mock_binary.format = expected_format
            result = analyze_binary(path)

            assert result["overall"]["format"] == expected_format.upper()
            assert len(result["sections"]) == 2
            assert result["overall"]["total_disk_bytes"] == 450 * 1024 + 320 * 1024

    def test_invalid_binary(self, mock_binary):
        with patch("lief.parse", return_value=None):
            with pytest.raises(ValueError, match="Unsupported or invalid"):
                analyze_binary("invalid")

    def test_zero_sizes(self, mock_binary):
        mock_binary.sections[0].size = 0
        mock_binary.sections[0].virtual_size = 0
        with patch("lief.parse", return_value=mock_binary):
            result = analyze_binary("zero.bin")
            assert all(s["disk_pct"] == 0.0 for s in result["sections"])

    def test_symbols_extraction(self, mock_binary):
        with patch("lief.parse", return_value=mock_binary):
            result = analyze_binary("syms.bin")
            symbols = result["symbols"]
            assert len(symbols) == 4  # 3 sized syms
            assert symbols[0]["name"] == "main"
            assert symbols[0]["size"] == 4096