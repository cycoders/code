import pytest
import lief
from unittest.mock import Mock, patch
from binary_explorer_tui.analyzer import BinaryAnalyzer


class TestBinaryAnalyzer:
    @patch("lief.parse")
    def test_parse_success(self, mock_parse):
        mock_binary = Mock()
        mock_binary.format.name = "ELF"
        mock_binary.header.machine = lief.MACHINE_TYPES.X86_64
        mock_binary.header.entrypoint = 0x401000
        mock_binary.libraries = ["libc.so"]
        mock_binary.sections = [Mock(name=".text", size=4096, content=b"aaa")]
        mock_binary.symbols = [Mock(name="main", value=0x401150, size=256)]
        mock_parse.return_value = mock_binary

        analyzer = BinaryAnalyzer("/fake.bin")
        assert analyzer.format == "ELF"
        assert analyzer.architecture == "x86_64"
        assert analyzer.entrypoint == 0x401000
        assert analyzer.libraries == ["libc.so"]
        assert len(analyzer.sections) == 1
        assert analyzer.sections[0]["entropy"] == pytest.approx(0.0)

    def test_parse_fail(self):
        with patch("lief.parse", return_value=None):
            with pytest.raises(ValueError):
                BinaryAnalyzer("/invalid")
