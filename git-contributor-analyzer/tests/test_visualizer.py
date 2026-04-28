import io
from unittest.mock import Mock

import pytest
from rich.console import Console

from git_contributor_analyzer.visualizer import print_table
from git_contributor_analyzer.types import ContributorStats


class TestVisualizer:
    @pytest.fixture
    def sample_stats(self):
        return [
            ContributorStats(
                "alice@example.com",
                "Alice",
                5,
                100,
                20,
                80,
                datetime.now(),
                datetime.now(),
                3,
                2,
                20.0,
            )
        ]

    def test_print_table(self, sample_stats):
        console = Mock(spec=Console)
        print_table(sample_stats, console)
        console.print.assert_called()

    def test_print_json(self, sample_stats):
        f = io.StringIO()
        # Redirect would be in real, but smoke test
        from git_contributor_analyzer.visualizer import print_json
        print_json(sample_stats)  # No crash
