from __future__ import annotations

import ast
from argparse import Namespace

from flake8.options.manager import OptionManager

from flake8_idom_hooks import __version__
from flake8_idom_hooks.run import (
    DEFAULT_COMPONENT_DECORATOR_PATTERN,
    DEFAULT_HOOK_FUNCTION_PATTERN,
    run_checks,
)

from .exhaustive_deps import HOOKS_WITH_DEPS


class Plugin:

    name = __name__
    version = __version__

    exhaustive_hook_deps: bool
    component_decorator_pattern: str
    hook_function_pattern: str

    def add_options(self, option_manager: OptionManager) -> None:
        option_manager.add_option(
            "--exhaustive-hook-deps",
            action="store_true",
            default=False,
            help=f"Whether to check hook dependencies for {', '.join(HOOKS_WITH_DEPS)}",
            dest="exhaustive_hook_deps",
            parse_from_config=True,
        )
        option_manager.add_option(
            "--component-decorator-pattern",
            nargs="?",
            default=DEFAULT_COMPONENT_DECORATOR_PATTERN,
            help=(
                "The pattern which should match the component decorators. "
                "Useful if you import the component decorator under an alias."
            ),
            dest="component_decorator_pattern",
            parse_from_config=True,
        )
        option_manager.add_option(
            "--hook-function-pattern",
            nargs="?",
            default=DEFAULT_HOOK_FUNCTION_PATTERN,
            help=(
                "The pattern which should match the name of hook functions. Best used "
                "if you have existing functions with 'use_*' names that are not hooks."
            ),
            dest="hook_function_pattern",
            parse_from_config=True,
        )

    def parse_options(self, options: Namespace) -> None:
        self.exhaustive_hook_deps = options.exhaustive_hook_deps
        self.component_decorator_pattern = options.component_decorator_pattern
        self.hook_function_pattern = options.hook_function_pattern

    def __call__(self, tree: ast.Module) -> list[tuple[int, int, str, type[Plugin]]]:
        return [
            error + (self.__class__,)
            for error in run_checks(
                tree,
                self.exhaustive_hook_deps,
                self.component_decorator_pattern,
                self.hook_function_pattern,
            )
        ]

    def __init__(self) -> None:
        # Hack to convince flake8 to accept plugins that are instances
        # see: https://github.com/PyCQA/flake8/pull/1674
        self.__init__ = self.__call__  # type: ignore
