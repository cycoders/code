import json
import random
import string
from typing import Any


def generate_sample_data(kind: str, approx_size: int = 1000) -> dict[str, Any]:
    """
    Generate representative data.

    simple: flat dict
    nested: tree w/ leaves (str/num/arr)
    array-heavy: long list of dicts
    """
    random.seed(42)  # Repro

    if kind == "simple":
        return {
            "id": 123456,
            "name": "".join(random.choices(string.ascii_letters, k=50)),
            "value": random.uniform(-1000, 1000),
            "tags": random.choices(string.ascii_lowercase, k=min(20, approx_size // 50)),
            "metadata": {f"key{i}": f"val{i}" for i in range(min(10, approx_size // 100))},
        }

    elif kind == "nested":
        def build(depth: int = 0, max_depth: int = 6, branch: int = 4) -> dict[str, Any]:
            if depth >= max_depth or random.random() < 0.4:
                return {
                    "str": "".join(random.choices(string.printable, k=random.randint(20, 200))),
                    "num": random.uniform(0, 1e6),
                    "arr": [random.randint(0, 255) for _ in range(random.randint(5, 50))],
                }
            children = [build(depth + 1, max_depth, branch) for _ in range(branch)]
            return {"children": children}

        tree = build()
        # Scale roughly
        scale = max(1, approx_size // 500)
        return {"root": [tree] * scale}

    elif kind == "array-heavy":
        items = [
            {"index": i, "label": f"item_{i}", "data": random.random()}
            for i in range(approx_size)
        ]
        return {"batch": items}

    else:
        raise ValueError(f"Unknown kind: {kind}. Use simple|nested|array-heavy")


if __name__ == "__main__":
    # Example gen
    data = generate_sample_data("nested", 5000)
    print(json.dumps(data, indent=2)[:500] + "...")  # Preview
