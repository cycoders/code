from crypto_agility_scanner.models import Finding
from pathlib import Path
import re

class Rule:
    def check(self, path: Path, text: str):
        raise NotImplementedError

class HardcodedHashRule(Rule):
    PATTERNS = [r"hashlib\.(md5|sha1)", r"SHA1|MD5"]
    def check(self, path, text):
        findings = []
        for m in re.finditer("|".join(self.PATTERNS), text):
            findings.append(Finding(path, text.count("\n", 0, m.start())+1, m.start(), m.group(), "critical", "Use hashlib.sha256 or BLAKE3", 0.95))
        return findings

RULES = [HardcodedHashRule()]