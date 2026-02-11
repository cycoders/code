from container_diff_cli.renderer import format_size, format_delta
from container_diff_cli.types import ImageDiff


def test_format_size():
    assert format_size(1024) == "1.0 KB"
    assert format_size(7500000) == "7.2 MB"


def test_format_delta():
    assert format_delta(300000) == "+293.0 KB"
    assert format_delta(-1024) == "-1.0 KB"


def test_diff_to_dict():
    diff = ImageDiff("i1", "i2", 1000, 2000, 1000, 1, 2, [], None, "l", "l", "a", "a")
    d = diff.to_dict()
    assert d["image1_name"] == "i1"
    assert "layer_deltas" in d
