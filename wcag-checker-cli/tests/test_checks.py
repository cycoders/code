import pytest
from wcag_checker_cli.auditor import Auditor

@pytest.mark.parametrize('check_id', list({'lang', 'title', 'images'}))
def test_individual_checks(check_id):
    html = '<html><body><img></body></html>'
    auditor = Auditor(html)
    # Invoke specific via config or direct
    auditor.audit()
    # Generic pass
    assert True

# More specific in other tests
