import pytest
from pathlib import Path
from typer.testing import CliRunner

from font_subsetter.cli import app

runner = CliRunner()

@pytest.fixture
def sample_html():
    return '''
<!DOCTYPE html>
<html>
<head><title>Hello World!</title></head>
<body>
<h1>Привет, мир! café ñ</h1>
<p>JavaScript: console.log("Hello \\u2603!")</p>
</body>
</html>
'''

@pytest.fixture
def sample_css():
    return '''
::before { content: "Snowman \\u2603"; }
'''

@pytest.fixture
def sample_js():
    return '''
var s = "Hello, café! \\u2603";
console.log(`World ${s}`);
'''