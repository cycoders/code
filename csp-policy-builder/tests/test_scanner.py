import pytest
from unittest.mock import Mock

from csp_policy_builder.scanner import Scanner
from csp_policy_builder.types import ScanConfig, Resource


def test_extract_inline(sample_config, mock_session):
    scanner = Scanner(sample_config)
    scanner.session = mock_session
    scanner._scan_url("https://test.com", 0)

    inline_script = next((r for r in scanner.resources if r.is_inline and r.directive == "script-src"), None)
    assert inline_script is not None
    assert inline_script.hash_value.startswith("'sha256-")


def test_extract_external(sample_config, mock_session):
    scanner = Scanner(sample_config)
    scanner.session = mock_session
    scanner._scan_url("https://test.com", 0)

    external = [r for r in scanner.resources if not r.is_inline]
    assert any("ex.com" in r.url for r in external)
    assert any(r.directive == "img-src" for r in external)


def test_limits(sample_config):
    config = ScanConfig(urls=["http://test"], max_depth=0, max_pages=1)
    scanner = Scanner(config)
    # Test no recursion
    assert len(scanner.scan()) == 0  # since mock not set
