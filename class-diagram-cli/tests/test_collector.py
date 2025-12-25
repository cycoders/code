import ast
import os
from pathlib import Path
tempfile

import pytest
from class_diagram_cli.collector import FileParser, CodebaseCollector
from class_diagram_cli.models import ClassInfo, Method


@pytest.fixture
def sample_py_file(tmp_path: Path) -> Path:
    code = '''
class Animal:
    age: int = 0

    def __init__(self):
        pass

    def speak(self):
        pass

class Dog(Animal):
    name = "woof"

    @staticmethod
    def bark():
        return "woof"
'''
    p = tmp_path / "sample.py"
    p.write_text(code)
    return p


def test_file_parser(sample_py_file: Path) -> None:
    parser = FileParser(sample_py_file)
    classes = parser.parse()

    assert len(classes) == 2
    animal = next(c for c in classes if c.name == "Animal")
    assert animal.module == "sample"
    assert len(animal.methods) == 2
    assert "age" in animal.attributes
    assert animal.bases == []

    dog = next(c for c in classes if c.name == "Dog")
    assert dog.bases == ["Animal"]
    assert len(dog.methods) == 1
    assert dog.methods[0].is_static
    assert "name" in dog.attributes


def test_codebase_collector(tmp_path: Path) -> None:
    (tmp_path / "mod1" / "a.py").parent.mkdir(parents=True)
    (tmp_path / "mod1" / "a.py").write_text("class A: pass")
    (tmp_path / "mod2.py").write_text("class B: pass")

    collector = CodebaseCollector(tmp_path)
    classes = collector.collect()

    assert len(classes) == 2
    assert {c.name for c in classes} == {"A", "B"}
    assert {c.module for c in classes} == {"a", "mod2"}


def test_exclude(tmp_path: Path) -> None:
    (tmp_path / "test.py").write_text("class Test: pass")
    (tmp_path / "src.py").write_text("class Src: pass")

    collector = CodebaseCollector(tmp_path, exclude=["**/test*.py"])
    classes = collector.collect()
    assert len(classes) == 1
    assert classes[0].name == "Src"


def test_syntax_error(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("def bad(): [")
    collector = CodebaseCollector(tmp_path)
    classes = collector.collect()
    assert len(classes) == 0  # No crash
