import json
from pathlib import Path
from typing import Dict, Any

import sbom_generator_cli  # for __version__

from .models import Component


def format_cyclonedx(
    components: list[Component], metadata: Dict[str, Any] | None = None
) -> str:
    """Serialize to CycloneDX 1.5 JSON."""
    if metadata is None:
        metadata = {"project": "unknown"}

    bom: Dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "metadata": {
            "component": {
                "name": metadata["project"],
                "type": "application",
            },
            "tools": [
                {"name": "sbom-generator-cli", "version": sbom_generator_cli.__version__}
            ],
        },
        "components": [
            {
                "type": c.type,
                "name": c.name,
                "version": c.version,
                "purl": c.purl,
            }
            for c in components
        ],
    }
    return json.dumps(bom, indent=2)


def format_spdx(
    components: list[Component], metadata: Dict[str, Any] | None = None
) -> str:
    """Serialize to SPDX 2.4 JSON."""
    import uuid

    if metadata is None:
        metadata = {"project": "unknown"}

    namespace = f"https://sbom-generator-cli/{uuid.uuid4().hex}"

    packages = []
    for i, c in enumerate(components):
        pkg_id = f"SPDXRef-Pkg-{i + 1}"
        packages.append(
            {
                "SPDXID": pkg_id,
                "name": c.name,
                "versionInfo": c.version,
                "SPDXIdentifier": c.purl,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": "NOASSERTION",
            }
        )

    doc: Dict[str, Any] = {
        "spdxVersion": "SPDX-2.4",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "documentNamespace": namespace,
        "name": metadata["project"],
        "packages": packages,
        "documentDescribes": [p["SPDXID"] for p in packages],
    }
    return json.dumps(doc, indent=2)


FORMATTERS = {
    "cyclonedx": format_cyclonedx,
    "spdx": format_spdx,
}
