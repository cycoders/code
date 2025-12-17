from gha_visualizer.analyzer import analyze
from gha_visualizer.models import Job


def test_analyze_basic():
    jobs = [
        Job(name="a", needs=[], steps=[{}] * 5),
        Job(name="b", needs=["a"], steps=[{}] * 30),
    ]
    stats = analyze(jobs)
    assert stats["jobs"] == 2
    assert stats["steps"] == 35
    assert stats["max_outdegree"] == 1
    assert stats["max_indegree"] == 1
    assert len(stats["issues"]) == 1  # long job
    assert "Long job 'b'" in stats["issues"][0]


def test_analyze_no_issues():
    jobs = [Job(name="short", needs=[], steps=[{}] * 10)]
    stats = analyze(jobs)
    assert stats["issues"] == []


def test_self_dependency():
    jobs = [Job(name="loop", needs=["loop"], steps=[])]
    stats = analyze(jobs)
    assert len(stats["issues"]) == 1
    assert "Self-dependency" in stats["issues"][0]