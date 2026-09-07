from license_compat_cli.matrix import CompatibilityMatrix

def test_basic():
    m = CompatibilityMatrix()
    assert m.check(None) == []