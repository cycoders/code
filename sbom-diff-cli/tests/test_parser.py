from pathlib import Path
from sbom_diff_cli.parser import load_sbom

def test_load_minimal_cyclonedx(tmp_path):
    p = tmp_path / "sbom.json"
    p.write_text('{"bomFormat":"CycloneDX","specVersion":"1.5"}')
    data = load_sbom(p)
    assert "components" in data