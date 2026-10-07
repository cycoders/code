import re
from datetime import datetime

def parse_combined(line: str):
    pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
    m = re.match(pattern, line)
    if not m: return None
    return {'ip': m.group(1), 'time': datetime.strptime(m.group(2), '%d/%b/%Y:%H:%M:%S %z'), 'method': m.group(3), 'path': m.group(4), 'status': int(m.group(5)), 'bytes': int(m.group(6))}