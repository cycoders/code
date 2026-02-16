import pytest
from unittest.mock import patch, MagicMock
from web_vitals_cli.auditor import audit_page


def test_audit_page_success(sample_lh_json):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(sample_lh_json), returncode=0)
        result = audit_page("https://test.com")
    assert result.overall_score == 0.92


def test_audit_page_timeout():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=1)
        audit_page("https://test.com", timeout=1)


def test_audit_page_node_missing():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc:
        mock_run.side_effect = FileNotFoundError
        audit_page("https://test.com")
    assert "Node.js/npx not found" in str(exc.value)