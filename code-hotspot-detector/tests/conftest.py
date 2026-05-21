import pytest
import tempfile
import git

@pytest.fixture
def sample_repo(tmp_path):
    repo = git.Repo.init(tmp_path)
    p = tmp_path / 'mod.py'
    p.write_text('def foo(x):\n    return x*2\n')
    repo.index.add([str(p)])
    repo.index.commit('init')
    return tmp_path