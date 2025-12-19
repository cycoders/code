import pytest
from git import Repo
from pathlib import Path


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    secret_file = repo_path / "secrets.env"
    secret_file.write_text("AWS_KEY=AKIA1234567890123456")
    repo.index.add([secret_file])
    repo.index.commit("Add secret")

    # Add high entropy
    entropy_file = repo_path / "token.txt"
    entropy_file.write_text("veryhighentropytoken1234567890abcdefghijklmnopqrstuvwxyz==")
    repo.index.add([entropy_file])
    repo.index.commit("Add entropy token")

    yield repo_path


@pytest.fixture
def clean_temp_dir(tmp_path: Path) -> Path:
    dir_path = tmp_path / "clean_dir"
    dir_path.mkdir()
    (dir_path / "readme.txt").write_text("No secrets here.")
    yield dir_path