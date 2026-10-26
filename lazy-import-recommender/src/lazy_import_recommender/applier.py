from pathlib import Path

def apply_changes(path: str, do_apply: bool):
    p = Path(path)
    if do_apply:
        print(f"Would rewrite {p}")
    else:
        print(f"Dry-run on {p}")