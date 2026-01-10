import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from websocket_tester.interactive import InteractiveShell


@pytest.mark.asyncio
async def test_parse_message_json():
    shell = InteractiveShell(MagicMock())
    msg = shell._parse_message('{"test": true}')
    assert msg == '{"test": true}'


@pytest.mark.asyncio
async def test_parse_message_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text('file content')
    shell = InteractiveShell(MagicMock())
    msg = shell._parse_message(f"@{p}")
    assert msg == "file content"


@pytest.mark.asyncio
@patch("asyncio.sleep")
async def test_cmd_replay(mock_sleep, tmp_path):
    shell = InteractiveShell(MagicMock())
    shell.client = MagicMock()
    shell.client.send = AsyncMock()
    p = tmp_path / "sess.jsonl"
    p.write_text('{"direction":"out","payload":{"replay":1}}\n')
    await shell.cmd_replay(str(p))
    shell.client.send.assert_called_once()
    mock_sleep.assert_called()


@pytest.mark.asyncio
async def test_cmd_send_no_client():
    shell = InteractiveShell(MagicMock())
    await shell.cmd_send("")
    # Logs error, no crash