import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_binary():
    binary = Mock()
    binary.format = "ELF"
    binary.header.machine = "x86_64"
    binary.libraries = ["libc.so.6", "libgcc_s.so.1"]

    sec_text = Mock()
    sec_text.name = ".text"
    sec_text.size = 450 * 1024
    sec_text.virtual_size = 450 * 1024
    sec_text.symbols = [
        Mock(name="main", size=4096),
        Mock(name="init", size=2048),
    ]

    sec_data = Mock()
    sec_data.name = ".data"
    sec_data.size = 320 * 1024
    sec_data.virtual_size = 512 * 1024
    sec_data.symbols = [Mock(name="global_var", size=1024)]

    binary.sections = [sec_text, sec_data]
    return binary