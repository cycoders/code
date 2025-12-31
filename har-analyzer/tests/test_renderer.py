from har_analyzer.renderer import render_stats, render_domains
import pytest
from unittest.mock import patch
from collections import Counter


class TestRenderer:
    @patch("rich.console.Console.print")
    def test_render_stats(self, mock_print):
        stats = {
            "total_requests": 100,
            "avg_response_time": 250.0,
            "p95_time": 1200.0,
            "total_transfer_size_kb": 2048.5,
            "error_rate_pct": 1.2,
        }
        render_stats(stats)
        mock_print.assert_called_once()

    @patch("rich.console.Console.print")
    def test_render_domains(self, mock_print):
        doms = Counter({"example.com": 50, "cdn.com": 30})
        render_domains(doms)
        mock_print.assert_called_once()