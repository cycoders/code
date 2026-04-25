import re
from typing import List
from .models import Hop

INF = float('inf')


def parse_traceroute_output(text: str) -> List[Hop]:
    """
    Parse standard traceroute output to list of Hops.

    Handles 1-3 probes per hop, * timeouts, ms values with/without !codes.
    """
    hops: List[Hop] = []
    lines = text.splitlines()
    for line in lines:
        line = line.rstrip()
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        hop_num = int(parts[0])
        ip = parts[1]
        probes = parts[2:5]  # up to 3 probes
        rtts = []
        for probe in probes:
            rtt_match = re.search(r'(\d+(?:\.\d+)?)', probe)
            if rtt_match:
                rtts.append(float(rtt_match.group(1)))
            else:
                rtts.append(INF)
        # Pad to 3 if fewer
        while len(rtts) < 3:
            rtts.append(INF)
        hops.append(Hop(hop_num=hop_num, ip=ip, rtts=rtts))
    return hops