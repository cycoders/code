import pytest

from formatter_preview.file_utils import PRETTIER_EXTS


def test_prettier_exts() -> None:
    assert ".json" in PRETTIER_EXTS
    assert ".py" not in PRETTIER_EXTS
