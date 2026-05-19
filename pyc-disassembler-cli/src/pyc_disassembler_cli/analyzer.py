import marshal, dis, types
from pathlib import Path
from .graph import build_cfg

def analyze_file(pyc_path: str, fmt: str = 'text') -> str:
    with open(pyc_path, 'rb') as f:
        f.read(16)  # header
        code = marshal.load(f)
    cfg = build_cfg(code)
    if fmt == 'text':
        return dis.dis(code, depth=2)
    return cfg.to_format(fmt)