import pytest
from chaos_proxy.config import Config, parse_duration, parse_bw, load_config_from_cli
from chaos_proxy.parser import parse_duration as parse_duration_alias


class TestParsers:
    @pytest.mark.parametrize(
        "input_str,expected",
        [("100ms", 0.1), ("1s", 1.0), ("500ms", 0.5), ("0", 0.0), ("0.25", 0.25)],
    )
    def test_parse_duration(self, input_str: str, expected: float) -> None:
        assert parse_duration(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [("100", 100.0), ("inf", float("inf")), ("50kbps", 50.0), ("0", 0.0)],
    )
    def test_parse_bw(self, input_str: str, expected: float) -> None:
        assert parse_bw(input_str) == expected


class TestConfigLoad:
    def test_cli_config(self) -> None:
        cfg = load_config_from_cli("example.com:80", 8080, "100ms", "50ms", 0.02, 0.01, "100")
        assert cfg.target_host == "example.com"
        assert cfg.target_port == 80
        assert cfg.latency == 0.1
        assert cfg.bw_kbps == 100.0
