from typing import List

from .git_client import GitClient
from .types import FileRisk


class RiskPredictor:
    """
    Computes risk scores using heuristics on git stats.
    """

    @classmethod
    def analyze(cls, gc: GitClient, source_ref: str, target_ref: str) -> List[FileRisk]:
        merge_base = gc.get_merge_base(source_ref, target_ref)
        target_changes = gc.get_changed_files(merge_base, target_ref)
        source_changes = gc.get_changed_files(merge_base, source_ref)
        overlapping = sorted(target_changes.intersection(source_changes))

        risks: List[FileRisk] = []
        for file_path in overlapping:
            ins_s, del_s = gc.get_change_stats(merge_base, source_ref, file_path)
            ins_t, del_t = gc.get_change_stats(merge_base, target_ref, file_path)
            change_size_s = ins_s + del_s
            change_size_t = ins_t + del_t
            hist_touches = gc.get_historical_merge_touches(file_path)

            overlap_ratio, change_size = cls._compute_overlap(change_size_s, change_size_t)
            risk_score, risk_level, suggestion = cls._compute_risk_score(
                overlap_ratio, hist_touches
            )

            risks.append(
                FileRisk(
                    path=file_path,
                    overlap_ratio=overlap_ratio,
                    change_size=change_size,
                    historical_conflicts=hist_touches,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    suggestion=suggestion,
                )
            )
        risks.sort(key=lambda r: r.risk_score, reverse=True)
        return risks

    @staticmethod
    def _compute_overlap(change_size_s: int, change_size_t: int) -> tuple[float, int]:
        change_size = change_size_s + change_size_t
        overlap_ratio = ((change_size_s * change_size_t) ** 0.5) / 1000.0
        return overlap_ratio, change_size

    @staticmethod
    def _compute_risk_score(
        overlap_ratio: float, hist_touches: int
    ) -> tuple[float, str, str]:
        history_factor = min(hist_touches / 10.0, 2.0)
        score = min(overlap_ratio * history_factor, 1.0)
        if score < 0.3:
            return score, "low", "Safe to merge."
        elif score < 0.7:
            return score, "medium", "Review changes carefully."
        else:
            return score, "high", "Rebase or resolve manually first."
