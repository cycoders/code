import pytest
from unittest.mock import Mock

from process_tree_tui.app import ProcessTreeApp


@pytest.mark.skip("TUI integration tests require display")
def test_app_init():
    app = ProcessTreeApp(refresh_interval=1.0, initial_search="test")
    assert app.refresh_interval == 1.0
    assert app.initial_search == "test"


@pytest.mark.parametrize("key,action", [
    ("q", "quit"),
    ("r", "refresh"),
    ("k", "kill_process"),
])
def test_bindings(key, action):
    app = ProcessTreeApp()
    assert any(b.key == key and b.action == action for b in app.BINDINGS)


def test_css_parsing():
    app = ProcessTreeApp()
    assert "#proc-tree" in app.CSS
    assert "dock: top" in app.CSS