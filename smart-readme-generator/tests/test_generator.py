import pytest
from smart_readme_generator.generator import render_readme


@pytest.fixture
def minimal_data():
    return {
        "project_name": "Test Project",
        "description": "Minimal test",
        "stacks": [],
        "features": [],
        "has_tests": False,
        "has_ci": False,
        "badges": [],
        "install_cmds": {},
        "usage_examples": {},
    }


def test_render_minimal(minimal_data):
    md = render_readme(minimal_data)
    assert "# Test Project" in md
    assert "Minimal test" in md
    assert "MIT License" in md


def test_render_with_stack():
    data = {
        "project_name": "FastAPI App",
        "description": "API server",
        "stacks": ["python-fastapi"],
        "features": ["FastAPI web framework"],
        "has_tests": True,
        "has_ci": True,
        "badges": [],
        "install_cmds": {"python-fastapi": "pip install"},
        "usage_examples": {"python-fastapi": "app = FastAPI()"},
    }
    md = render_readme(data)
    assert "FastAPI" in md
    assert "Test suite" in md
    assert "CI/CD" in md
    assert "pip install" in md
