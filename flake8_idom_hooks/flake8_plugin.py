import ast

from typing import List, Tuple, Type

from flake8_idom_hooks import __version__

from .utils import ErrorVisitor
from .rules_of_hooks import RulesOfHooksVisitor
from .exhaustive_deps import ExhaustiveDepsVisitor


class Plugin:

    name = __name__
    version = __version__

    _visitor_types: List[Type[ErrorVisitor]] = [
        RulesOfHooksVisitor,
        ExhaustiveDepsVisitor,
    ]

    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree

    def run(self) -> List[Tuple[int, int, str, Type["Plugin"]]]:
        errors = []
        for vtype in self._visitor_types:
            visitor = vtype()
            visitor.visit(self._tree)
            errors.extend(visitor.errors)
        return [(line, col, msg, self.__class__) for line, col, msg in errors]
