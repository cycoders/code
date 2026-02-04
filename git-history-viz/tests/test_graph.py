from git_history_viz.graph import topological_sort
from git_history_viz.parser import parse_repo


class TestGraph:
    def test_topo_sample(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 10)
        order = topological_sort(commits)
        assert len(order) == 4
        # Roots first (indeg 0)
        assert order[0] in [c.sha for c in commits.values() if not c.parents]

    def test_topo_linear(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 2)
        order = topological_sort(commits)
        # Older before newer
        assert order[0] != list(commits)[-1].sha

    def test_empty(self):
        from {} import topological_sort
        assert topological_sort({}) == []
