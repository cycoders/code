import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

def parse_run(stdout_file: Path) -> Dict[str, List[str]]:
    """Parse pytest -v stdout to {nodeid: [outcomes]}."""
    if not stdout_file.exists():
        return {}

    stdout = stdout_file.read_text()
    results = defaultdict(list)

    # Matches: tests/test.py::TestCls::test_meth PASSED[ 10%]
    #          tests/test.py::test_func[param] FAILED
    pattern = re.compile(
        r"^([a-zA-Z0-9_/.-]+?)(::[^ \[\]]+?)\s+(PASSED|FAILED|SKIPPED|XPASSED|XFAILED)(?:\s+\[.*?\])?$"
    )

    for line in stdout.splitlines():
        match = pattern.match(line)
        if match:
            nodeid = match.group(1) + match.group(2)
            outcome = match.group(3)
            results[nodeid].append(outcome)

    return dict(results)