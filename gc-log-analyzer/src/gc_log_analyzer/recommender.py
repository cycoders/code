from typing import List, Dict
from .parser import GCPause

def recommend(pauses: List[GCPause]) -> Dict[str, str]:
    stats = {}
    long_pauses = [p for p in pauses if p.duration_ms > 200]
    if long_pauses:
        stats["recommendation"] = "Consider increasing -Xms and enabling G1GC with -XX:MaxGCPauseMillis=150"
    else:
        stats["recommendation"] = "Current GC settings appear healthy"
    return stats