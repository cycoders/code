import json
from pathlib import Path

import git
import pytest
from git import GitCommandError

from perf_regression_detector.baseline import load_baseline, save_baseline


@pytest.fixture
def baseline_file(tmp_path):
    path = tmp_path / ".perf-regression" / "baseline.json"
    return path


def test_save_load(baseline_file):
    results = {"test": {"wall_time": {"mean": 1.0, "std": 0.1}}}
    save_baseline(results, baseline_file)
    loaded = load_baseline()
    assert loaded == results


def test_load_git_ref(tmp_path, baseline_file):
    repo = git.Repo.init(tmp_path)
    baseline_file.parent.mkdir()
    results = {"test": {"wall_time": {"mean": 1.0}}}
    baseline_file.write_text(json.dumps(results))
    repo.index.add([str(baseline_file)])
    repo.index.commit("init")

    loaded = load_baseline("HEAD")
    assert loaded == results

    with pytest.raises(GitCommandError):
        load_baseline("badref")