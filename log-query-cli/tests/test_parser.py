import pendulum
from log_query_cli.parser import parse_line, DEFAULT_PATTERNS


class TestParser:
    def test_json_parse(self):
        line = '{"level":"ERROR","service":"db","message":"boom","ts":"2024-01-01T00:00:00Z"}'
        result = parse_line(line)
        assert result["level"] == "ERROR"
        assert result["service"] == "db"
        assert pendulum.parse("2024-01-01T00:00:00Z") == result.get("ts")

    def test_regex_parse(self):
        line = "2024-01-01T12:00:00Z INFO app: User login success"
        result = parse_line(line)
        assert result["timestamp"] == pendulum.parse("2024-01-01T12:00:00Z")
        assert result["level"] == "INFO"
        assert result["service"] == "app"

    def test_fallback(self):
        line = "Plain text log"
        result = parse_line(line)
        assert result["raw_line"] == "Plain text log"

    def test_empty_line(self):
        assert parse_line(" ") is None
        assert parse_line("\n") is None

    def test_custom_patterns(self):
        custom = [r"(?P<custom>foo): (?P<msg>bar)"]
        result = parse_line("foo: bar baz", custom)
        assert result["custom"] == "foo"
        assert result["msg"] == "bar baz"