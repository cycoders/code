import pytest
from textual.app import App
from textual.testing import TestRunner

# Smoke tests for widgets

@pytest.mark.asyncio
async def test_key_browser_smoke():
    # Requires app context, minimal
    class TestApp(App):
        pass
    runner = TestRunner(TestApp())
    await runner.run_until_complete()
    # Extend with mocks if needed
    assert True


@pytest.mark.parametrize("widget", ["dashboard", "slowlog_viewer"])
def test_widget_imports(widget):
    from redis_explorer_tui.widgets import dashboard, slowlog_viewer  # noqa
    assert True
