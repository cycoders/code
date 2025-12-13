import pytest
from git_churn_analyzer.models import GitFileChange


def test_git_file_change_post_init():
    change = GitFileChange("file.py", 10, 5)
    assert change.lines_changed == 15


@pytest.mark.parametrize("ins,del_,expected", [(0, 0, 0), (1, 0, 1), (0, 2, 2)])
def test_lines_changed(ins, del_, expected):
    change = GitFileChange("f", ins, del_)
    assert change.lines_changed == expected
