from pathlib import Path
from dotenv_linter.parser import parse_env

def test_basic_parse(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux")
    assert len(parse_env(f)) == 2