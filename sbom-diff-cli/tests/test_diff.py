from sbom_diff_cli.diff import compute_diff

def test_empty_diff():
    assert compute_diff({}, {}) == {"added": [], "removed": [], "changed": []}

def test_added_component():
    old = {"components": []}
    new = {"components": [{"name": "requests", "version": "2.31.0"}]}
    result = compute_diff(old, new)
    assert len(result["added"]) == 1