from crypto_agility_scanner.rules import HardcodedHashRule
from pathlib import Path

def test_rule_matches():
    rule = HardcodedHashRule()
    f = rule.check(Path("x.py"), "hashlib.sha1(data)")
    assert len(f) == 1