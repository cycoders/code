"""Test data loader."""

from unicode_picker_tui.data import DataLoader


def test_load_chars():
    loader = DataLoader()
    loader.load()
    assert len(loader.chars) > 100000
    assert len(loader.blocks) > 300
    assert "Basic Latin" in loader.blocks
