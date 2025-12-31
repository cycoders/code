import builtins
import json
import os
import runpy
import sys
import traceback
from pathlib import Path
from typing import Any

from startup_profiler.profiler import ImportProfiler


def main() -> None:
    output_file = os.environ["STARTUP_PROFILER_OUTPUT"]
    profiler = ImportProfiler()
    builtins.__import__ = profiler.monkeypatched_import()
    data: Dict[str, Any] = {}
    try:
        script_path = sys.argv[1] if len(sys.argv) > 1 else None
        if not script_path:
            raise ValueError("No script path provided")
        runpy.run_path(script_path, run_name="__main__")
        data = profiler.get_timings()
    except Exception as e:
        data = {"error": str(e), "traceback": "".join(traceback.format_exception(type(e), e, e.__traceback__))}
    finally:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
