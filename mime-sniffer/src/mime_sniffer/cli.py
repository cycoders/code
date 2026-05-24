import argparse
import json
import sys
from pathlib import Path

from .detector import sniff

def main() -> None:
    parser = argparse.ArgumentParser(prog="mime-sniffer")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    mime = sniff(args.path)
    if mime is None:
        print("unknown", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({"path": str(args.path), "mime": mime}))
    else:
        print(mime)

if __name__ == "__main__":
    main()