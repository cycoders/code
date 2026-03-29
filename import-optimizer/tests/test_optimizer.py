import libcst as cst
import pytest
from import_optimizer.optimizer import process_module


@pytest.mark.parametrize(
    "input_code,expected_code",
    [
        # Unused removal
        (
            "import unused\nprint('hi')",
            "print('hi')\n",
        ),
        # Used keep
        (
            "import os\nprint(os.path.join('/'))",
            "import os\n\nprint(os.path.join('/'))\n",
        ),
        # Grouping & sorting
        (
            "from typing import List\nimport random\nfrom .local import foo\nimport os",
            "from typing import List\n\nimport os\nimport random\n\nfrom .local import foo\n",
        ),
        # Future
        (
            "from __future__ import annotations\nimport sys",
            "from __future__ import annotations\n\nimport sys\n",
        ),
        # Star keep
        (
            "from os import *\nprint(whatever)",
            "from os import *\n\nprint(whatever)\n",
        ),
        # Multi import
        (
            "import a, b\nfrom foo import x, y",
            "import a\nimport b\n\nfrom foo import x, y\n",
        ),
    ],
)


def test_process_module(input_code, expected_code):
    module = cst.parse_module(input_code)
    new_module = process_module(module)
    # Normalize whitespace for test
    assert new_module.code.strip() == expected_code.strip()