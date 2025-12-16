import pytest
from pathlib import Path

from dupe_code_finder.blocks import extract_blocks
from dupe_code_finder.tokenizer import TokenPos


@pytest.fixture
def mock_tokens():
    return [
        ("DEF", 1),
        ("ID", 1),
        ("LPAREN", 1),
        ("ID", 1),
        ("RPAREN", 1),
        ("COLON", 1),
        ("RETURN", 1),
        ("ID", 1),
        ("TIMES", 1),
        ("NUM", 1),
    ] * 4, ["line1\n", "line2\n"]


def test_extract_blocks(mock_tokens):
    norm_tokens, lines = mock_tokens
    path = Path("test.py")
    blocks = extract_blocks(path, norm_tokens, lines, min_size=5, step=3)
    assert len(blocks) > 0
    block = blocks[0]
    assert isinstance(block, CodeBlock)
    assert block.path == "test.py"
    assert "DEF ID LPAREN ID RPAREN COLON RETURN" in block.token_str
