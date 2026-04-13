from disk_usage_tui.utils import format_bytes


def test_format_bytes():
    assert format_bytes(0) == "0.0 B"
    assert format_bytes(1023) == "1,023.0 B"
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(1024**3 * 1.5) == "1,500.0 MiB"