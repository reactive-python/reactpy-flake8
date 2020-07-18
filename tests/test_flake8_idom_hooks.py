import ast
from pathlib import Path

import pytest

from flake8_idom_hooks import Plugin


case_file_asts = {}
for path in (Path(__file__).parent / "cases").rglob("*.py"):
    with path.open() as f:
        tree = ast.parse(f.read(), path.name)
        case_file_asts[path.name[:-3]] = tree


expectations = {
    "hook_in_conditional": [(7, 39, "hooks cannot be used in conditionals")]
}


@pytest.mark.parametrize(
    "tree, expected_errors",
    [(case_file_asts[name], expectations[name]) for name in case_file_asts],
)
def test_flake8_idom_hooks(tree, expected_errors):
    actual_errors = Plugin(tree).run()
    assert [(ln, col, msg) for ln, col, msg, p_type in actual_errors] == expected_errors
