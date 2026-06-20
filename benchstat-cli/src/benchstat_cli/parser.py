import json
from pathlib import Path

def parse_file(path):
    p = Path(path)
    if p.suffix == '.json':
        return json.loads(p.read_text())
    # simple line parser for Go/Python text output
    data = []
    for line in p.read_text().splitlines():
        if 'ns/op' in line or 'ops/sec' in line:
            parts = line.split()
            data.append({'name': parts[0], 'ns_per_op': float(parts[1])})
    return {'benchmarks': data}