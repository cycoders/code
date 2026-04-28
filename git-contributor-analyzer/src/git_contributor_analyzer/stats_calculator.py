from collections import defaultdict
from datetime import date, timedelta, datetime
from typing import List

from .types import CommitInfo, ContributorStats


def calculate_stats(commits: List[CommitInfo]) -> List[ContributorStats]:
    author_commits = defaultdict(list)
    for commit in commits:
        author_commits[commit.author_email].append(commit)

    stats_list: List[ContributorStats] = []
    for email, comms in author_commits.items():
        if not comms:
            continue
        name = comms[0].author_name
        total_insertions = sum(c.insertions for c in comms)
        total_deletions = sum(c.deletions for c in comms)
        net_loc = total_insertions - total_deletions
        dates = sorted({c.authored_date.date() for c in comms})
        active_days = len(dates)
        max_streak = _compute_max_streak(dates)
        first_contrib = min(comms, key=lambda c: c.authored_date).authored_date
        last_contrib = max(comms, key=lambda c: c.authored_date).authored_date
        avg_ins = total_insertions / len(comms) if comms else 0

        stats_list.append(
            ContributorStats(
                email=email,
                name=name,
                commit_count=len(comms),
                total_insertions=total_insertions,
                total_deletions=total_deletions,
                net_loc=net_loc,
                first_contrib=first_contrib,
                last_contrib=last_contrib,
                active_days=active_days,
                max_streak=max_streak,
                avg_insertions_per_commit=round(avg_ins, 1),
            )
        )
    return sorted(stats_list, key=lambda s: s.net_loc, reverse=True)


def _compute_max_streak(dates: List[date]) -> int:
    if len(dates) == 0:
        return 0
    dates = sorted(dates)
    max_streak = current_streak = 1
    prev_date = dates[0]
    for d in dates[1:]:
        if d == prev_date + timedelta(days=1):
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
        prev_date = d
    return max_streak
