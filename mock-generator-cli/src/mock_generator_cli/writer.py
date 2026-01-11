import black
from typing import Set, Optional
from pathlib import Path


def generate_test_code(
    module_name: str,
    func_name: str,
    calls: Set[str],
    is_method: bool,
    class_name: Optional[str] = None,
) -> str:
    """Generate Black-formatted pytest test code."""
    patches = sorted(calls)
    patches_str = "\n    ".join(f"mocker.patch('{call}', return_value=None)" for call in patches)
    if not patches_str:
        patches_str = "pass"

    if is_method:
        test_name = f"test_{class_name}_{func_name}"
        import_line = f"from {module_name} import {class_name}"
        if func_name == "__init__":
            call_lines = f"    instance = {class_name}()  # Calls __init__"
        else:
            call_lines = f"""    instance = {class_name}()
    instance.{func_name}()"""
    else:
        test_name = f"test_{func_name}"
        import_line = f"from {module_name} import {func_name}"
        call_lines = f"    {func_name}()"

    source = f"""import pytest

{import_line}


def {test_name}(mocker):
    {patches_str}
{call_lines}
"""

    mode = black.FileMode(target_versions={black.TargetVersion.PY311})
    return black.format_str(source, mode=mode)