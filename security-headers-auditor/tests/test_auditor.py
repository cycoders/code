import pytest
from unittest.mock import patch
from security_headers_auditor.auditor import Auditor


class TestAuditor:
    @pytest.mark.parametrize("score,expected", [
        (9.0, "A"),
        (6.5, "B"),
        (4.5, "C"),
        (2.5, "D"),
        (1.0, "F"),
    ])
    def test_grade(self, score, expected):
        auditor = Auditor()
        assert auditor._compute_grade(score) == expected

    def test_audit_json(self, mock_webscanner, capsys):
        auditor = Auditor()
        auditor.audit("https://test.com", output_json=True)
        captured = capsys.readouterr()
        assert '"grade"' in captured.out
