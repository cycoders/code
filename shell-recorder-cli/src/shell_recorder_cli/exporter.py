import json
from pathlib import Path


def export_md(path: Path, output: Path, title: str = "Terminal Session") -> None:
    """Concat stdout to MD bash block."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    stdout_all = "".join(e["stdout"] for e in data[1:] if "stdout" in e).rstrip("\n")
    md_content = f"""# {title}

**Duration:** {data[0]['duration']:.1f}s | **Size:** {len(data[0]['events_count'])} chunks

```bash
{stdout_all}
```
"""
    output.write_text(md_content)
