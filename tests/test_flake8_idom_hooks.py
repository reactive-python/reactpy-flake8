import ast
from pathlib import Path

from flake8.options.manager import OptionManager

from flake8_idom_hooks import Plugin

options_manager = OptionManager("test", "0.0.0")
Plugin.add_options(options_manager)


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
                expected_errors.add((lineno, col_offset, message, Plugin))

    options, filenames = options_manager.parse_args(["--exhaustive-hook-deps"])
    Plugin.parse_options(options)

    assert set(Plugin(tree).run()) == expected_errors
