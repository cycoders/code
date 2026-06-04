import sys
import json

def parse_logs(paths):
    events = []
    for path in paths:
        if path == "-":
            fh = sys.stdin
        else:
            fh = open(path)
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                ev = {"raw": line, "ts": "1970-01-01T00:00:00Z"}
            if "ts" not in ev:
                ev["ts"] = "1970-01-01T00:00:00Z"
            events.append(ev)
        if path != "-":
            fh.close()
    return events