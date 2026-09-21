from typosquat_auditor.scanner import load_packages

def test_ignores_short_tokens():
    assert 'a' not in load_packages(Path('/tmp/dummy.txt')) # handled by caller