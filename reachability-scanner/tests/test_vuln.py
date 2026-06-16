from reachability_scanner.vuln import filter_reachable

def test_filter():
    reachable = {"foo.bar", "baz"}
    vulns = [{"id": "V1", "functions": ["foo.bar"]}, {"id": "V2", "functions": ["other"]}]
    assert filter_reachable(reachable, vulns) == ["V1"]