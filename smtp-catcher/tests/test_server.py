import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from aiosmtpd.testing import SMTPTestTransaction

from smtp_catcher.server import EmailHandler
from smtp_catcher.storage import save_email


@pytest.mark.asyncio
async def test_handler(tmp_data_dir):
    handler = EmailHandler(tmp_data_dir)

    # Mock envelope
    class MockEnvelope:
        content = b"Subject: Test\n\nBody"
        mail_from = "sender@test.com"
        rcpt_tos = ["rcpt@test.com"]

    class MockSession:
        peer = ("127.0.0.1", 1234)

    class MockServer:
        pass

    with patch("smtp_catcher.storage.save_email") as mock_save:
        await handler.handle_DATA(MockServer(), MockSession(), MockEnvelope())
        mock_save.assert_called_once()
        args = mock_save.call_args[0]
        assert args[1]["sender"] == "sender@test.com"
        assert args[1]["recipients"] == ["rcpt@test.com"]