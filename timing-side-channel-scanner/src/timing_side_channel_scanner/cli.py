import argparse
from pathlib import Path
from rich.console import Console
from .scanner import scan_path

console = Console()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    findings = scan_path(args.path)
    for f in findings:
        console.print(f"[red]{f}")