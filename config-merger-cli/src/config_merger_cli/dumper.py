import json
import sys
from pathlib import Path
from typing import Dict, Any

import yaml
import tomlkit


def dump_config(data: Dict[str, Any], output: str, fmt: str) -> None:
    """Dump dict to file/stdout in given format, preserving order."""
    out_path = Path(output)
    if output == '-':
        fh = sys.stdout
        close = False
    else:
        fh = open(out_path, 'w', encoding='utf-8')
        close = True

    try:
        if fmt == 'yaml':
            yaml.dump(
                data, fh,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
                allow_unicode=True
            )
        elif fmt == 'json':
            json.dump(data, fh, indent=2, sort_keys=False, ensure_ascii=False)
        elif fmt == 'toml':
            toml_doc = tomlkit.document(data)
            fh.write(tomlkit.dumps(toml_doc))
        else:
            raise ValueError(f"Unsupported output format: {fmt!r}")
        if not output.endswith(('yaml', 'yml', 'json', 'toml')):
            fh.write('\n')  # pretty
    finally:
        if close:
            fh.close()