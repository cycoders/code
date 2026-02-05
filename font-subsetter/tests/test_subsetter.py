import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from font_subsetter.subsetter import subset_single_font

@pytest.fixture
def mock_font_path(tmp_path):
    orig_font = tmp_path / "test.ttf"
    orig_font.write_bytes(b"fake font data")
    return orig_font

@pytest.fixture
def codepoints():
    return {ord('A'), ord('B'), 0x2603}

@patch('fontTools.ttLib.TTFont')
@patch('fontTools.subset.Subsetter')
def test_subset_single_font(mock_subsetter, mock_ttfont, mock_font_path, codepoints, tmp_path):
    mock_font = MagicMock()
    mock_ttfont.return_value = mock_font

    mock_subsetter_instance = MagicMock()
    mock_subsetter.return_value = mock_subsetter_instance
    mock_subsetter_instance.subset.return_value = None

    out_path = tmp_path / "test.subset.ttf"

    stat = subset_single_font(mock_font_path, codepoints, out_path)

    assert len(stat) == 6
    assert stat[0] == "test.ttf"
    assert stat[4] > 0  # glyphs_used

    mock_subsetter_instance.populate.assert_called_once_with(codepoints=list(codepoints))
    mock_font.save.assert_called_once_with(out_path)