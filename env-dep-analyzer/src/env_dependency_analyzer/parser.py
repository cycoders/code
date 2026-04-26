import re
import yaml
from pathlib import Path
from typing import Set, List, Tuple

REF_PATTERN = re.compile(
    r'\$([A-Z_][A-Z0-9_]*)|\'\$\{([A-Z_][A-Z0-9_]*)(?::[^}]*)?\}\'',
    re.IGNORECASE
)

# More precise for quoted etc, but simplified
REF_PATTERN = re.compile(r'\$([A-Z0-9_]+)|\$\{([A-Z0-9_]+)(?::[^}]*)?\}')

def extract_refs(value: str) -> Set[str]:
    """Extract env var refs from string. Supports $VAR, ${VAR}, ${VAR:-def}."""
    refs = set()
    for m in REF_PATTERN.finditer(value):
        refs.add(m.group(1) or m.group(2))
    return refs

def parse_dotenv(path: Path, visited: Set[Path]) -> Tuple[Set[str], List[Tuple[str, str]]]:
    if path in visited:
        return set(), []
    visited.add(path)
    defined: Set[str] = set()
    edges: List[Tuple[str, str]] = []
    try:
        content = path.read_text(encoding='utf-8')
    except Exception:
        return set(), []
    for line in content.splitlines():
        line = line.split('#', 1)[0].strip()
        if '=' not in line:
            continue
        parts = line.split('=', 1)
        key = parts[0].strip()
        value = parts[1].strip()
        # Unquote
        if value and value[0] in "'\"\" and value[0] == value[-1]:
            value = value[1:-1]
        defined.add(key)
        refs = extract_refs(value)
        for ref in refs:
            edges.append((key, ref))
    return defined, edges

def parse_compose(path: Path, visited: Set[Path]) -> Tuple[Set[str], List[Tuple[str, str]]]:
    if path in visited:
        return set(), []
    visited.add(path)
    defined: Set[str] = set()
    edges: List[Tuple[str, str]] = []
    try:
        data = yaml.safe_load(path.read_text())
    except Exception:
        return set(), []
    services = data.get('services', {})
    for svc, conf in services.items():
        # environment dict
        env = conf.get('environment')
        if isinstance(env, dict):
            for key, val in env.items():
                if isinstance(val, str):
                    defined.add(key)
                    refs = extract_refs(val)
                    for ref in refs:
                        edges.append((key, ref))
        elif isinstance(env, list):
            for item in env:
                if isinstance(item, str) and '=' in item:
                    k, v = item.split('=', 1)
                    k, v = k.strip(), v.strip()
                    if v[0] in "'\" and v[0] == v[-1]:
                        v = v[1:-1]
                    defined.add(k)
                    refs = extract_refs(v)
                    for ref in refs:
                        edges.append((k, ref))
        # env_file recursive
        env_files = conf.get('env_file')
        if isinstance(env_files, str):
            env_files = [env_files]
        if isinstance(env_files, list):
            base = path.parent
            for ef_str in env_files:
                ef_path = base / ef_str.strip()
                if ef_path.is_file():
                    defi, edg = parse_dotenv(ef_path, visited)
                    defined.update(defi)
                    edges.extend(edg)
    return defined, edges

def scan_directory(root: Path) -> Tuple[Set[str], List[Tuple[str, str]], List[Path]]:
    """Scan dir for configs, return defined, edges, files."""
    config_files = []
    rootp = Path(root)
    for globpat in ['*.env*', 'docker-compose*.y*ml', 'compose*.y*ml']:
        config_files.extend(rootp.rglob(globpat))
    all_defined: Set[str] = set()
    all_edges: List[Tuple[str, str]] = []
    visited: Set[Path] = set()
    for fpath in config_files:
        if fpath.name.endswith('.env') or '.env.' in fpath.name:
            defi, edg = parse_dotenv(fpath, visited)
        elif 'docker-compose' in fpath.name or 'compose' in fpath.name:
            defi, edg = parse_compose(fpath, visited)
        else:
            continue
        all_defined.update(defi)
        all_edges.extend(edg)
    return all_defined, all_edges, list(config_files)
