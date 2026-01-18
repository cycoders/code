from pathlib import Path
from typing import List


def parse_copy_patterns(dockerfile_path: Path) -> List[str]:
    """
    Parse Dockerfile for COPY/ADD src patterns (non --from).

    Handles: COPY [--chown=..] src1 src2.. dest
    Skips: COPY --from=..
    Assumes single-line instructions (95% cases).
    """
    patterns: List[str] = []

    with dockerfile_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if not parts or parts[0].upper() not in ("COPY", "ADD"):
                continue

            j = 1
            flags = []
            while j < len(parts) and parts[j].startswith("--"):
                flags.append(parts[j])
                j += 1

            if any(flag.startswith("--from") for flag in flags):
                continue

            srcs = parts[j : -1]  # All but last (dest)
            if srcs:
                patterns.extend(srcs)

    return list(set(patterns))  # Dedupe


# For tests
import textwrap


def dockerfile_content(example: str) -> Path:
    """Test helper."""
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(suffix="Dockerfile", delete=False) as f:
        f.write(textwrap.dedent(example).encode())
        f.flush()
        return Path(f.name)
