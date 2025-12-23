import builtins
import os
import sys
import time
from collections import defaultdict
from typing import Dict, Any


def profile_imports(script_path: str) -> Dict[str, Any]:
    """
    Profile imports in a Python script.

    Returns dict with 'total_startup_time', 'modules': {mod: {'inclusive', 'exclusive', 'deps'}}.
    """
    script_dir = os.path.dirname(os.path.abspath(script_path))
    script_name = os.path.basename(script_path)

    # Insert script dir to path
    old_path = sys.path[:]
    sys.path.insert(0, script_dir)

    graph: Dict[str, Dict[str, float]] = defaultdict(dict)
    load_times: Dict[str, float] = {}

    original_import = builtins.__import__

    def timed_import(name: str, *args: Any, **kwargs: Any) -> Any:
        caller_frame = sys._getframe(1)
        caller_name = caller_frame.f_globals.get("__name__", "<unknown>")

        start = time.perf_counter()
        mod = original_import(name, *args, **kwargs)
        dt = time.perf_counter() - start

        # Only time first load
        if name not in sys.modules:
            load_times[name] = dt
            graph[caller_name][name] = dt

        return mod

    builtins.__import__ = timed_import  # type: ignore

    try:
        start_total = time.perf_counter()
        with open(script_path, "r", encoding="utf-8") as f:
            source = f.read()
        code = compile(source, script_path, "exec")
        exec(code, {"__name__": "__main__", "__file__": script_path})
        total_time = time.perf_counter() - start_total
    except SyntaxError as e:
        raise ValueError(f"Syntax error in {script_path}: {e}") from e
    except Exception:
        # Still return partial stats if imports succeeded
        total_time = time.perf_counter() - start_total
        raise
    finally:
        builtins.__import__ = original_import
        sys.path[:] = old_path

    # Compute exclusive times
    all_modules = set(load_times)
    exclusive: Dict[str, float] = {}
    for mod in all_modules:
        children = graph[mod]
        excl = load_times.get(mod, 0.0)
        for child in children:
            excl -= load_times.get(child, 0.0)
        exclusive[mod] = max(0.0, excl)

    data = {
        "total_startup_time": total_time,
        "modules": {
            mod: {
                "inclusive": load_times.get(mod, 0.0),
                "exclusive": exclusive.get(mod, 0.0),
                "deps": dict(graph[mod]),
            }
            for mod in all_modules
        },
    }
    return data
