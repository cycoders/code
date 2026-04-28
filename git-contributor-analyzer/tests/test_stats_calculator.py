import pytest
from datetime import date, timedelta, datetime

from git_contributor_analyzer.stats_calculator import calculate_stats, _compute_max_streak
from git_contributor_analyzer.types import CommitInfo, ContributorStats


class TestStatsCalculator:
    @pytest.mark.parametrize(
        "dates, expected",
        [
            ([], 0),
            ([date(2023, 1, 1)], 1),
            ([date(2023, 1, 1), date(2023, 1, 2)], 2),
            ([date(2023, 1, 1), date(2023, 1, 3), date(2023, 1, 4)], 2),
            ([date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3), date(2023, 1, 5)], 3),
        ],
    )
    def test_compute_max_streak(self, dates, expected):
        assert _compute_max_streak(dates) == expected

    def test_calculate_stats(self):
        commit1 = CommitInfo(
            "abc123",
            "Alice",
            "alice@example.com",
            datetime(2023, 1, 1),
            10,
            2,
            1,
        )
        commit2 = CommitInfo(
            "def456",
            "Alice",
            "alice@example.com",
            datetime(2023, 1, 3),
            20,
            5,
            2,
        )
        commits = [commit1, commit2]
        stats = calculate_stats(commits)
        assert len(stats) == 1
        s = stats[0]
        assert s.name == "Alice"
        assert s.commit_count == 2
        assert s.total_insertions == 30
        assert s.net_loc == 23
        assert s.active_days == 2
        assert s.max_streak == 1
