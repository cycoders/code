import pytest
from binary_explorer_tui.utils import entropy, human_size, hex_addr


class TestUtils:
    def test_entropy_low(self):
        assert entropy(b"aaa") == pytest.approx(0.0, abs=1e-6)

    def test_entropy_high(self):
        assert entropy(b"abc") == pytest.approx(math.log2(3), abs=1e-6)

    def test_entropy_empty(self):
        assert entropy(b"") == 0.0

    def test_human_size(self):
        assert human_size(0) == "0.0 B"
        assert human_size(1023) == "1023.0 B"
        assert human_size(1024) == "1.0 KiB"
        assert human_size(1024**2) == "1.0 MiB"

    def test_hex_addr(self):
        assert hex_addr(0) == "0x0000000000000000"
        assert hex_addr(0x123456789abcdef) == "0x0123456789abcdef"
