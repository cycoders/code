import pytest
from pathlib import Path
import pandas as pd

from pii_anonymizer.utils import load_dataframe, save_dataframe


def test_load_save_csv(tmp_path: Path):
    sample_path = tmp_path / "test.csv"
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    df.to_csv(sample_path, index=False)

    loaded = load_dataframe(sample_path, "csv")
    assert pd.DataFrame.equals(loaded.reset_index(drop=True), df.reset_index(drop=True))

    out_path = tmp_path / "out.csv"
    save_dataframe(loaded, out_path, "csv")
    assert out_path.exists()


def test_load_jsonl(tmp_path: Path):
    sample_path = tmp_path / "test.jsonl"
    data = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    pd.DataFrame(data).to_json(sample_path, orient="records", lines=True)

    loaded = load_dataframe(sample_path, "json")
    assert len(loaded) == 2
