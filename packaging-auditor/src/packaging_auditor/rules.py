from pathlib import Path

def check_metadata(data, root):
    proj = data.get("project", {})
    findings = []
    if not proj.get("name"):
        findings.append({"severity": "error", "message": "project.name is required"})
    if not proj.get("version"):
        findings.append({"severity": "error", "message": "project.version is required"})
    if not proj.get("readme"):
        findings.append({"severity": "warning", "message": "readme recommended for PyPI"})
    return findings

RULES = [check_metadata]