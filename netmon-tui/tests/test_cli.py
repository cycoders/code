import sys
from unittest.mock import patch

import typer

from netmon_tui.cli import main


def test_cli_help(monkeypatch, capsys):
    """--help works."""

    monkeypatch.setattr(sys, "argv", ["netmon-tui", "--help"])

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "Refresh interval" in captured.out


@patch("netmon_tui.app.NetmonApp.run")
def test_cli_launch(mock_run):
    """Launches app."""

    main(refresh=0.5)
    mock_run.assert_called_once()