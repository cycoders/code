from dataclasses import dataclass

@dataclass
class UnsafePattern:
    name: str
    severity: str
    message: str
    def matches(self, node):
        # simplified libcst attribute/call matching
        return False

UNSAFE_PATTERNS = [
    UnsafePattern("pickle.load", "critical", "Replace with safer format (msgpack/orjson)"),
    UnsafePattern("yaml.unsafe_load", "critical", "Use yaml.safe_load"),
]