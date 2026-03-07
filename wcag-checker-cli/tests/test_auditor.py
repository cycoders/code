import pytest
from wcag_checker_cli.auditor import Auditor
from wcag_checker_cli.types import Issue


def test_audit_good(good_html):
    auditor = Auditor(good_html)
    auditor.audit()
    assert len(auditor.issues_list) == 0
    assert auditor.get_score() == 'A'


def test_missing_lang(bad_lang_html):
    auditor = Auditor(bad_lang_html)
    auditor.audit()
    issues = auditor.issues_list
    assert len(issues) >= 1
    lang_issue = next(i for i in issues if i.id == 'missing-lang')
    assert lang_issue.severity == 'error'


def test_img_no_alt(bad_img_html):
    auditor = Auditor(bad_img_html)
    auditor.audit()
    issues = auditor.issues_list
    assert any(i.id == 'img-no-alt' for i in issues)


def test_score_scaling():
    auditor = Auditor('<html></html>')
    auditor.audit()
    assert auditor.get_score() == 'F'  # Many issues
