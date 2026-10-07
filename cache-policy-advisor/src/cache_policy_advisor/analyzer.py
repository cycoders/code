from collections import defaultdict
from cache_policy_advisor.parser import parse_combined

def analyze_logs(path, fmt, window):
    hits, misses, bytes_saved = 0, 0, 0
    with open(path) as f:
        for line in f:
            rec = parse_combined(line)
            if rec and rec['status'] == 304: hits += 1
            else: misses += 1
    return {'hit_rate': hits / (hits + misses) if hits + misses else 0, 'recommendation': 'Increase max-age to 86400'}