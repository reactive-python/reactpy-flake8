from __future__ import annotations

import ast
from argparse import Namespace

from flake8.options.manager import OptionManager

from flake8_idom_hooks import __version__
from flake8_idom_hooks.run import run_checks


class Plugin:

    name = __name__
    version = __version__

    exhaustive_hook_deps: bool

    @classmethod
    def add_options(cls, option_manager: OptionManager) -> None:
        option_manager.add_option(
            "--exhaustive-hook-deps",
            action="store_true",
            default=False,
            dest="exhaustive_hook_deps",
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options: Namespace) -> None:
        cls.exhaustive_hook_deps = getattr(options, "exhaustive_hook_deps", False)

    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree

    def run(self) -> list[tuple[int, int, str, type[Plugin]]]:
        return [
            error + (self.__class__,)
            for error in run_checks(self._tree, self.exhaustive_hook_deps)
        ]
