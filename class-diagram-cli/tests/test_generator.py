import textwrap
from pathlib import Path

import pytest
from rich.console import Console
from class_diagram_cli.generator import MermaidGenerator
from class_diagram_cli.models import ClassInfo, Method


@pytest.fixture
def sample_classes() -> list[ClassInfo]:
    return [
        ClassInfo(
            name="Animal",
            module="zoo",
            bases=[],
            methods=[Method("speak")],
            attributes=["age"],
        ),
        ClassInfo(
            name="Dog",
            module="zoo",
            bases=["Animal"],
            methods=[Method("bark", is_static=True)],
            attributes=["name"],
        ),
    ]


def test_generator(sample_classes, tmp_path: Path) -> None:
    console = Console()
    gen = MermaidGenerator(sample_classes, console)
    diagram = gen.generate()

    expected = textwrap.dedent(
        """
        classDiagram
            direction TB
            class `Animal` {{
                +age
                +speak(){}
            }}
            class `Dog` {{
                +name
                #bark(){}
            }}
            `Dog` <|-- `Animal` : "extends"
        """
    ).strip()

    assert diagram.strip() == expected


def test_unresolved_base(sample_classes) -> None:
    sample_classes[1].bases.append("Unknown")
    console = Console(record=True)
    gen = MermaidGenerator(sample_classes, console)
    gen.generate()
    assert "Unresolved bases" in console.export_text()


def test_name_clash() -> None:
    classes = [
        ClassInfo(name="Clash", module="m1"),
        ClassInfo(name="Clash", module="m2"),
    ]
    console = Console(record=True)
    gen = MermaidGenerator(classes, console)
    gen.generate()
    assert "Name clashes" in console.export_text()
