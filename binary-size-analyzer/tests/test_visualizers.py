import io
from unittest.mock import patch

import pytest
import rich.console

from binary_size_analyzer.visualizers import (
    human_size,
    spark_pct,
    print_overall_panel,
    print_sections_table,
)


class TestVisualizers:
    @pytest.fixture
    def sample_data(self):
        return {
            "overall": {
                "format": "ELF",
                "architecture": "x86_64",
                "total_disk_bytes": 1024 * 1024,
                "total_mem_bytes": 2 * 1024 * 1024,
                "sections_count": 5,
                "libs_count": 2,
            },
            "sections": [
                {
                    "name": ".text",
                    "disk_size": 500 * 1024,
                    "disk_pct": 48.8,
                    "mem_size": 500 * 1024,
                    "mem_pct": 24.4,
                    "symbols_count": 10,
                }
            ],
        }

    def test_human_size(self):
        assert human_size(1024) == "1.0 KiB"
        assert human_size(1500 * 1024) == "1.5 MiB"
        assert human_size(0) == "0 B"

    def test_spark_pct(self):
        assert spark_pct(0) == " "
        assert spark_pct(50) == "▄"
        assert spark_pct(100) == "█"

    @patch("rich.console.Console.print")
    def test_print_overall_panel(self, mock_print, sample_data):
        print_overall_panel(sample_data, "both")
        mock_print.assert_called_once()

    @patch("rich.table.Table")
    def test_print_sections_table(self, mock_table, sample_data):
        print_sections_table(sample_data["sections"], "both", 10)
        mock_table.return_value.add_row.assert_called()