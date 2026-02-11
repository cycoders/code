import json

from sbom_generator_cli.formatter import format_cyclonedx, format_spdx
from sbom_generator_cli.models import Component


comp = Component(name="test", version="1.0", purl="pkg:test/test@1.0")


def test_cyclonedx():
    bom_str = format_cyclonedx([comp])
    bom = json.loads(bom_str)
    assert bom["bomFormat"] == "CycloneDX"
    assert len(bom["components"]) == 1
    assert bom["components"][0]["purl"] == "pkg:test/test@1.0"


def test_spdx():
    bom_str = format_spdx([comp])
    bom = json.loads(bom_str)
    assert bom["spdxVersion"] == "SPDX-2.4"
    assert len(bom["packages"]) == 1
    assert bom["packages"][0]["name"] == "test"


def test_dedupe():
    from sbom_generator_cli.generator import dedupe_components
    dups = [comp, Component(name="test", version="1.0", purl="pkg:test/test@1.0")]
    unique = dedupe_components(dups)
    assert len(unique) == 1
