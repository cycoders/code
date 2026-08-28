from crypto_agility_scanner.models import Finding
from pathlib import Path

def test_finding_creation():
    f = Finding(Path("a.py"), 10, 3, "md5", "critical", "use sha256", 0.9)
    assert f.severity == "critical"