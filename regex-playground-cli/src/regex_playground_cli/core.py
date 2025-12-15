import re
from collections import namedtuple
from typing import List, Tuple, Optional

MatchResult = namedtuple("MatchResult", ["start", "end", "groups"])


class RegexTester:
    def __init__(self, pattern: str, flags: int):
        self.pattern = pattern
        self.flags_int = flags
        self.flags_str = self._flags_to_str(flags)
        try:
            self.compiled = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex '{pattern}': {e.msg}") from e

    def _flags_to_str(self, flags: int) -> str:
        flag_map = {
            re.I: "i (case-insensitive)",
            re.M: "m (multiline)",
            re.S: "s (dotall)",
            re.X: "x (verbose)",
        }
        active = [desc for flag, desc in flag_map.items() if flags & flag]
        return ", ".join(active) or "none"

    @classmethod
    def from_input(cls, s: str) -> "RegexTester":
        s = s.strip()
        parts = s.rsplit("/", 1)
        pattern = parts[0]
        flags_str = parts[1] if len(parts) > 1 else ""
        if pattern.startswith("/"):
            pattern = pattern[1:]
        flags = 0
        flag_map = {
            "i": re.I,
            "I": re.I,
            "m": re.M,
            "M": re.M,
            "s": re.S,
            "S": re.S,
            "x": re.X,
            "X": re.X,
        }
        for char in flags_str:
            if char in flag_map:
                flags |= flag_map[char]
            elif char:
                raise ValueError(f"Unknown flag '{char}'")
        return cls(pattern, flags)

    def test(self, text: str) -> List[MatchResult]:
        results = []
        for match in self.compiled.finditer(text):
            groups = match.groups()
            results.append(MatchResult(match.start(), match.end(), groups))
        return results

    def __repr__(self):
        return f"RegexTester(pattern='{self.pattern}', flags='{self.flags_str}')"
