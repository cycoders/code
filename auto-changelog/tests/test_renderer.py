import pytest
from auto_changelog.renderer import Renderer
from auto_changelog.types import Commit
from auto_changelog.config import DEFAULT_CONFIG


@pytest.fixture
def sample_commits():
    return [
        Commit("abc", "feat", "ui", "add button"),
        Commit("def", "fix", None, "bug fix"),
    ]


def test_render(sample_commits):
    md = Renderer.render(sample_commits, DEFAULT_CONFIG)
    assert "# Changelog" in md
    assert "## Added" in md
    assert "- add button(ui) [abc]" in md
    assert "## Fixed" in md
    assert "- bug fix [def]" in md