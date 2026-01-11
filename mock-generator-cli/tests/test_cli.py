import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from mock_generator_cli.cli import app


DEMO_CONTENT = """
import os
from json import loads

def foo():
    os.path.join('a')
    loads('{{}}')

class MyClass:
    def method(self):
        os.makedirs('dir')
"""


@pytest.fixture
def demo_file(tmp_path: Path):
    file = tmp_path / "demo.py"
    file.write_text(DEMO_CONTENT)
    return file


class TestCLI:
    runner = CliRunner()

    def test_generate_function(self, demo_file):
        result = self.runner.invoke(app, [f"{demo_file}:foo"])
        assert result.exit_code == 0
        assert "mocker.patch('os.path.join'" in result.stdout
        assert "mocker.patch('json.loads'" in result.stdout
        assert "test_foo" in result.stdout

    def test_generate_method(self, demo_file):
        result = self.runner.invoke(app, [f"{demo_file}:MyClass.method"])
        assert result.exit_code == 0
        assert "mocker.patch('os.makedirs'" in result.stdout
        assert "test_MyClass_method" in result.stdout
        assert "instance = MyClass()" in result.stdout

    def test_file_not_found(self):
        result = self.runner.invoke(app, ["nonexistent.py:foo"])
        assert result.exit_code == 1
        assert "File not found" in result.stderr

    def test_not_found(self, demo_file):
        result = self.runner.invoke(app, [f"{demo_file}:missing"])
        assert result.exit_code == 1
        assert "not found" in result.stderr