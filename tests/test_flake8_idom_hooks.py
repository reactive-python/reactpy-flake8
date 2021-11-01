import ast
from pathlib import Path

from flake8_idom_hooks import run_checks


def test_flake8_idom_hooks():
    path_to_case_file = Path(__file__).parent / "hook_usage_test_cases.py"
    with path_to_case_file.open() as file:
        # save the file's AST
        file_content = file.read()
        tree = ast.parse(file_content, path_to_case_file.name)

        # find 'error' comments to construct expectations
        expected_errors = set()
        for index, line in enumerate(file_content.split("\n")):
            lstrip_line = line.lstrip()
            if lstrip_line.startswith("# error:"):
                lineno = index + 2  # use 2 since error should be on next line
                col_offset = len(line) - len(lstrip_line)
                message = line.replace("# error:", "", 1).strip()
                expected_errors.add((lineno, col_offset, message))
    assert set(run_checks(tree, exhaustive_hook_deps=True)) == expected_errors
