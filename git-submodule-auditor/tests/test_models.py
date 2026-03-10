from git_submodule_auditor.models import Submodule, submodules_to_dict


def test_submodule_dataclass():
    sub = Submodule(
        path="test",
        url="https://ex.com/repo",
        current_commit="abc123",
        target_branch="main",
        is_dirty=False,
        outdated=True,
        days_behind=200,
        issues=["old-commit"]
    )
    assert sub.path == "test"
    assert sub.outdated


def test_to_dict():
    sub = Submodule("path", "url", "commit", None, True, False, 10, ["issue"])
    dct = submodules_to_dict([sub])
    assert len(dct) == 1
    assert dct[0]["path"] == "path"
    assert dct[0]["issues"] == ["issue"]
