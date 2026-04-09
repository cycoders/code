from review_checklist_cli.output import render_md
from review_checklist_cli.core import ChecklistItem


def test_render_md():
    items = [
        ChecklistItem("Test Title", "Test desc", "high", "cmd"),
    ]
    md = render_md(items)
    assert "# Code Review Checklist" in md
    assert "Test Title" in md
    assert "`cmd`" in md


def test_print_console(capsys):
    # Hard to test rich, but smoke
    from review_checklist_cli.output import print_console
    items = []
    print_console(items)
    captured = capsys.readouterr()
    assert "Checklist" in captured.out