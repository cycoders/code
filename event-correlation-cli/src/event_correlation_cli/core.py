from collections import defaultdict
from datetime import timedelta
from dateutil.parser import isoparse

def correlate(events, keys, window_str):
    window = timedelta(seconds=int(window_str.rstrip("s")))
    index = defaultdict(list)
    for ev in events:
        for k in keys:
            if k in ev:
                index[(k, ev[k])].append(ev)
    chains = []
    for bucket in index.values():
        bucket.sort(key=lambda e: isoparse(e["ts"]))
        for i, e1 in enumerate(bucket):
            chain = [e1]
            t0 = isoparse(e1["ts"])
            for e2 in bucket[i+1:]:
                if isoparse(e2["ts"]) - t0 > window:
                    break
                chain.append(e2)
            if len(chain) > 1:
                chains.append({"score": len(chain), "events": chain})
    return sorted(chains, key=lambda c: -c["score"])[:10]