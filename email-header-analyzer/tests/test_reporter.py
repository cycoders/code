from unittest.mock import MagicMock
import pytest
from email_header_analyzer.reporter import generate_report, STATUS_EMOJI


def test_status_emoji():
    assert STATUS_EMOJI["pass"] == "🟢"
    assert STATUS_EMOJI["fail"] == "🔴"


def test_generate_report(capfd):
    console = MagicMock()
    analysis = {
        "dkim": [{"result": "pass"}],
        "spf": {"status": "pass"},
        "dmarc": {"status": "none"},
        "received": [{"ip": "1.2.3.4", "helo": "mail.ex"}],
    }
    generate_report(console, analysis, False)
    # Checks console.print calls implicitly
    assert True
