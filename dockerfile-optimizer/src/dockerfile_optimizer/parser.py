import re
from dataclasses import dataclass
from typing import List


@dataclass
class Instruction:
    """Represents a single Dockerfile instruction."""

    command: str
    args: str
    line_number: int
    original_line: str


def parse_dockerfile(file_path: str) -> List[Instruction]:
    """
    Parse a Dockerfile into a list of Instructions.

    Handles comments, blank lines, JSON/shell args.

    >>> parse_dockerfile('path/to/Dockerfile')
    """
    instructions: List[Instruction] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.rstrip()
            # Strip inline comments
            hash_pos = line.find("#")
            if hash_pos != -1:
                line = line[:hash_pos].rstrip()
            line = line.strip()
            if not line:
                continue
            # Match INSTRUCTION [args]
            match = re.match(r"^([A-Z][A-Z0-9]*)(?:\s+(.*))?$", line)
            if match:
                cmd, args = match.groups()
                args = args or ""
                instructions.append(
                    Instruction(cmd, args, line_num, raw_line.strip())
                )
    return instructions
