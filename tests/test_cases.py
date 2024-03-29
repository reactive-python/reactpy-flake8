import ast
import sys
from pathlib import Path

import flake8
import pytest
from flake8.options.manager import OptionManager

import reactpy_flake8
from reactpy_flake8.flake8_plugin import Plugin

HERE = Path(__file__).parent


def setup_plugin(args):
    if flake8.__version_info__ >= (6,):
        options_manager = OptionManager(
            version="",
            plugin_versions="",
            parents=[],
            formatter_names=[],
        )
    elif flake8.__version_info__ >= (5,):
        options_manager = OptionManager(
            version="",
            plugin_versions="",
            parents=[],
        )
    elif flake8.__version_info__ >= (4,):
        options_manager = OptionManager(
            version="",
            parents=[],
            prog="",
        )
    elif flake8.__version_info__ >= (3, 7):
        options_manager = OptionManager(
            version="",
            parents=[],
            prog="",
        )
    else:
        raise RuntimeError("Unsupported flake8 version")

    plugin = Plugin()
    plugin.add_options(options_manager)

    if flake8.__version_info__ >= (5,):
        options = options_manager.parse_args(args)
    else:
        options, _ = options_manager.parse_args(args)

    plugin.parse_options(options)

    return plugin


@pytest.mark.parametrize(
    "options_args, case_file_name",
    [
        (
            "",
            "hook_usage.py",
        ),
        (
            "",
            "no_exhaustive_deps.py",
        ),
        pytest.param(
            "",
            "match_statement.py",
            marks=pytest.mark.skipif(
                sys.version_info < (3, 10),
                reason="Match statement only in Python 3.10 and above",
            ),
        ),
        (
            "--exhaustive-hook-deps",
            "exhaustive_deps.py",
        ),
        (
            r"--component-decorator-pattern ^(component|custom_component)$",
            "custom_component_decorator_pattern.py",
        ),
        (
            r"--hook-function-pattern ^_*use_(?!ignore_this)\w+$",
            "custom_hook_function_pattern.py",
        ),
    ],
)
def test_reactpy_flake8(options_args, case_file_name):
    case_file = Path(__file__).parent / "cases" / case_file_name
    # save the file's AST
    file_content = case_file.read_text()

    # find 'error' comments to construct expectations
    expected_errors = set()
    for index, line in enumerate(file_content.split("\n")):
        lstrip_line = line.lstrip()
        if lstrip_line.startswith("# error:"):
            lineno = index + 2  # use 2 since error should be on next line
            col_offset = len(line) - len(lstrip_line)
            message = line.replace("# error:", "", 1).strip()
            expected_errors.add((lineno, col_offset, message, reactpy_flake8.Plugin))

    plugin = setup_plugin(options_args.split())
    actual_errors = plugin(ast.parse(file_content, case_file_name))
    assert set(actual_errors) == expected_errors
