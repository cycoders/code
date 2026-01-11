import os
import json


def foo(path: str) -> tuple[str, dict]:
    """Example function with external calls."""
    p = os.path.join(path, "file.txt")
    data = json.loads('{{ "key": "value" }}')
    return p, data


class MyClass:
    """Example class."""

    def __init__(self):
        os.mkdir("/tmp/test")

    def method(self, dir_path: str):
        os.makedirs(dir_path, exist_ok=True)
        print("done")
