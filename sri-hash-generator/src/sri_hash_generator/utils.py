from pathlib import Path

def find_html_files(root: Path):
    return list(root.rglob("*.html"))