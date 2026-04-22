import fnmatch
import glob
from pathlib import Path
from typing import Dict, List, Optional

import libcst

from .config import Config
from .parser import extract_imports
from .types import Violation


def get_package_prefix(root: Path, src_dir: str, file_path: Path) -> str:
    rel_path = file_path.relative_to(root)
    parts = rel_path.parts[:-1]  # exclude filename
    if parts and parts[0] == src_dir:
        prefix_parts = parts[1:]
    else:
        prefix_parts = parts
    return ".".join(prefix_parts) + "." if prefix_parts else ""


def analyze(root: Path, config: Config) -> List[Violation]:
    prefix_to_layer: Dict[str, str] = {}
    for layer in config.layers:
        for prefix in layer.package_prefixes:
            if prefix in prefix_to_layer:
                raise ValueError(f"Ambiguous prefix '{prefix}' in layers {prefix_to_layer[prefix]} and {layer.name}")
            prefix_to_layer[prefix] = layer.name

    py_files = glob.glob(str(root / config.src_dir / "**/*.py"), recursive=True)
    violations: List[Violation] = []

    for py_file_str in py_files:
        py_file = Path(py_file_str)
        rel_glob = str(py_file.relative_to(root))
        if any(fnmatch.fnmatch(rel_glob, pattern) for pattern in config.ignore_globs):
            continue

        importer_prefix = get_package_prefix(root, config.src_dir, py_file)
        importer_layer = prefix_to_layer.get(importer_prefix)
        if not importer_layer:
            continue  # Skip unlayered files

        try:
            code = py_file.read_text(encoding="utf-8")
        except Exception:
            continue  # Graceful skip unreadable

        imports = extract_imports(code)
        importer_layer_obj = next(l for l in config.layers if l.name == importer_layer)

        for mod_name, line in imports:
            imported_layer = None
            for prefix, lyr in prefix_to_layer.items():
                if mod_name.startswith(prefix):
                    imported_layer = lyr
                    break

            if imported_layer:
                if imported_layer in importer_layer_obj.forbidden_layers:
                    violations.append(
                        Violation(
                            file=py_file,
                            line=line,
                            from_layer=importer_layer,
                            to_layer=imported_layer,
                            severity="error",
                            message="forbidden dependency",
                        )
                    )
                elif imported_layer not in importer_layer_obj.allowed_layers:
                    violations.append(
                        Violation(
                            file=py_file,
                            line=line,
                            from_layer=importer_layer,
                            to_layer=imported_layer,
                            severity="warning",
                            message="not explicitly allowed",
                        )
                    )
            elif not config.allow_third_party:
                violations.append(
                    Violation(
                        file=py_file,
                        line=line,
                        from_layer=importer_layer,
                        to_layer=None,
                        severity="warning",
                        message="third-party import",
                    )
                )

    return violations