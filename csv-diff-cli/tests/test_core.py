import pytest
from csv_diff_cli.core import diff_csvs


@pytest.mark.parametrize("keys,tol,exp_changes", [
    ([], 0.0, 2),  # ordered: age/salary Bob
    (["id"], 0.0, 2),  # key match
    (["id"], 1000.0, 1),  # tol covers salary diff
])
def test_diff_csvs(sample_df1, sample_df2, keys, tol, exp_changes):
    # Write to temp files
    import tempfile
import io

    f1 = io.StringIO(sample_df1.write_csv())
    f2 = io.StringIO(sample_df2.write_csv())

    result = diff_csvs(f1.getvalue(), f2.getvalue(), keys, [], tol)

    assert len(result["cell_changes"]) == exp_changes
    assert result["stats"]["only_left"] == 0
    assert result["stats"]["only_right"] == 1


def test_empty_files():
    result = diff_csvs("", "", [], [], 0.0)
    assert result["stats"]["rows_left"] == 0
    assert result["stats"]["rows_right"] == 0