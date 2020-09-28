import ast
from pkg_resources import (
    get_distribution as _get_distribution,
    DistributionNotFound as _DistributionNotFound,
)
from typing import List, Tuple, Type

from .utils import ErrorVisitor
from .rules_of_hooks import RulesOfHooksVisitor
from .exhaustive_deps import ExhaustiveDepsVisitor

try:
    __version__ = _get_distribution(__name__).version
except _DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0"


class Plugin:

    name = __name__
    version = __version__
    options = None

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
