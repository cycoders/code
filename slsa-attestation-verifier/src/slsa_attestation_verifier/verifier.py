from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class VerificationResult:
    valid: bool
    reason: str = ""

def verify_attestation(attestation_path: str, artifact: str, policy=None) -> VerificationResult:
    data = json.loads(Path(attestation_path).read_text())
    # Simplified DSSE/in-toto check (production would use sigstore + in-toto)
    if "payload" not in data:
        return VerificationResult(False, "Invalid DSSE envelope")
    if policy:
        return evaluate(data, artifact, policy)
    return VerificationResult(True)
