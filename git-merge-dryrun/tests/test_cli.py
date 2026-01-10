import typer
from pathlib import Path
from git_merge_dryrun.cli import app
from git_merge_dryrun.merger import detect_conflicts, get_merge_base


class TestCLI:
    def test_merge_command_help(self, mocker):
        runner = typer.testing.CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Preview merging TARGET into SOURCE" in result.stdout

    def test_merge_with_conflicts(self, git_repo: Path, mocker, tmp_path: Path):
        # cd to repo
        prev_cwd = Path.cwd()
        try:
            os.chdir(git_repo)
            runner = typer.testing.CliRunner()
            result = runner.invoke(app, ["branch2", "branch1"])
            assert result.exit_code == 0
            assert "Conflicts" in result.stdout
        finally:
            os.chdir(prev_cwd)

    def test_invalid_repo(self, tmp_path: Path, mocker):
        runner = typer.testing.CliRunner()
        result = runner.invoke(app, ["fake"], cwd=tmp_path)
        assert result.exit_code == 1
        assert "Not a git repository" in result.stdout