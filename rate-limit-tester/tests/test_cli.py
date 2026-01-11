import sys
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rate_limit_tester.cli import app

runner = CliRunner()


def test_discover_help():
    result = runner.invoke(app, ["discover", "--help"])
    assert result.exit_code == 0
    assert "Discover rate limits" in result.stdout


@pytest.mark.asyncio
async def test_main_no_args():
    with patch("sys.argv", ["rate-limit-tester"]):
        # Would invoke test_cmd with default
        pass
