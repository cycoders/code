import pytest
from hashlib import sha384
from security_headers_auditor.csp_generator import CSPGenerator
from security_headers_auditor.utils import compute_sha384


class TestCSPGenerator:
    def test_generate_empty_html(self):
        gen = CSPGenerator()
        policy = gen.generate("<html></html>", "https://example.com")
        assert "default-src 'self'" in policy
        assert "frame-ancestors 'none'" in policy

    def test_inline_script_hash(self):
        html = '<html><script>alert("test");</script></html>'
        content = 'alert("test");'
        expected_hash = f"'sha384-{sha384(content.encode('utf-8')).hexdigest()}'"
        gen = CSPGenerator()
        policy = gen.generate(html, "https://example.com")
        assert "script-src" in policy
        assert expected_hash in policy

    def test_external_src_domain(self):
        html = '<html><script src="/static/app.js"></script></html>'
        gen = CSPGenerator()
        policy = gen.generate(html, "https://example.com")
        assert "https://example.com*" in policy
