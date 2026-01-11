import pytest
from pathlib import Path


@pytest.fixture
def tmp_bins(tmp_path: Path):
    """Create sample binary files."""
    data1 = b"\x00\x11\x22" * 20 + b"\xff" * 10  # 90 bytes
    data2 = b"\x00\x11\x23" * 20 + b"\x00" * 10  # 90 bytes, 20 changes

    f1 = tmp_path / "file1.bin"
    f2 = tmp_path / "file2.bin"
    f1_short = tmp_path / "short.bin"
    f_empty = tmp_path / "empty.bin"

    f1.write_bytes(data1)
    f2.write_bytes(data2)
    f1_short.write_bytes(data1[:30])
    f_empty.write_bytes(b"")

    return f1, f2, f1_short, f_empty