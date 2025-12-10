from typing import Dict, Set, List, Any
from polars import DataFrame


def compare_schemas(
    df1: DataFrame, df2: DataFrame, ignore: Set[str]
) -> Dict[str, Any]:
    """
    Compare column schemas between two DataFrames.

    Returns:
        Dict with only_in_1, only_in_2, dtype_mismatches.
    """
    cols1: Set[str] = set(df1.columns) - ignore
    cols2: Set[str] = set(df2.columns) - ignore
    common: Set[str] = cols1 & cols2

    only_in_1: List[str] = sorted(cols1 - cols2)
    only_in_2: List[str] = sorted(cols2 - cols1)

    dtype1 = {c: str(df1[c].dtype) for c in common}
    dtype2 = {c: str(df2[c].dtype) for c in common}
    dtype_mismatches: Dict[str, tuple[str, str]] = {
        c: (dtype1[c], dtype2[c]) for c in common if dtype1[c] != dtype2[c]
    }

    return {
        "only_in_1": only_in_1,
        "only_in_2": only_in_2,
        "dtype_mismatches": dtype_mismatches,
    }