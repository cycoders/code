from pydantic import BaseModel

class Policy(BaseModel):
    fail_on_critical: bool = True

def evaluate(sbom, policy: Policy):
    return []