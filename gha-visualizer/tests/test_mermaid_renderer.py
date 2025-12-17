import textwrap
from gha_visualizer.mermaid_renderer import generate_mermaid
from gha_visualizer.models import Job


def test_generate_mermaid_basic():
    jobs = [
        Job(name="start", needs=[], steps=[{"run": "echo hi"}]),
        Job(name="end", needs=["start"], steps=[]),
    ]
    mermaid = generate_mermaid(jobs)
    assert "flowchart TD" in mermaid
    assert "start[\"start\"]" in mermaid
    assert "end[\"end\"]" in mermaid
    assert "start --> end" in mermaid
    assert "start_steps [" in mermaid


def test_job_id_sanitization():
    jobs = [Job(name="job-1.with.dot", needs=[], steps=[])]
    mermaid = generate_mermaid(jobs)
    assert "job_1_with_dot[" in mermaid  # sanitized


def test_strategy_badge():
    jobs = [Job(name="test", needs=[], steps=[], strategy={})]
    mermaid = generate_mermaid(jobs)
    assert "test [matrix]" in mermaid