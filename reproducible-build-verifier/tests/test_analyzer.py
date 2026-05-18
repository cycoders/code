from reproducible_build_verifier.analyzer import BuildAnalyzer

def test_detects_timestamp_difference():
    a = BuildAnalyzer()
    findings = a.analyze('build1', 'build2')
    assert any(f['type'] == 'timestamp' for f in findings)

def test_empty_inputs():
    a = BuildAnalyzer()
    assert a.analyze('/nonexistent', '/nonexistent2') == []