import pytest
from pathlib import Path

import env_usage_scanner.parsers as parsers
import env_usage_scanner.models as models


@pytest.mark.parametrize(
    "lang,content,expected_vars",
    [
        ("python", "os.getenv('DB_URL')", ["DB_URL"]),
        ("javascript", "process.env.DATABASE_URL", ["DATABASE_URL"]),
        ("go", 'os.Getenv("REDIS_HOST")', ["REDIS_HOST"]),
        ("shell", "$API_KEY", ["API_KEY"]),
        ("dockerfile", "ENV FOO=bar", ["FOO"]),
        ("compose", "environment: { DB: url }", ["DB"]),
    ],
)
def test_parse_file(lang: str, content: str, expected_vars: list[str], temp_dir: Path):
    file_path = temp_dir / "test.txt"
    file_path.write_text(content)
    usages = parsers.parse_file(file_path, lang)
    assert {u.var_name for u in usages} == set(expected_vars)
