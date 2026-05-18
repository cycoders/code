import argparse
import sys
from .parser import parse_gc_log
from .analyzer import compute_stats
from .recommender import recommend

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze GC logs")
    parser.add_argument("logfile", help="Path to GC log")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    try:
        with open(args.logfile) as f:
            pauses = parse_gc_log(f)
        stats = compute_stats(pauses)
        recs = recommend(pauses)
        if args.format == "json":
            import json
            print(json.dumps({**stats, **recs}, indent=2))
        else:
            print(f"Pauses: {stats['total_pauses']}, Max: {stats.get('max_pause_ms', 0):.1f}ms")
            print(recs.get("recommendation", ""))
    except FileNotFoundError:
        print("Log file not found", file=sys.stderr)
        sys.exit(1)