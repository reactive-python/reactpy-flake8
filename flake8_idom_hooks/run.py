from __future__ import annotations

import ast

from .utils import ErrorVisitor
from .exhaustive_deps import ExhaustiveDepsVisitor
from .rules_of_hooks import RulesOfHooksVisitor


def run_checks(
    tree: ast.Module,
    exhaustive_hook_deps: bool,
) -> list[tuple[int, int, str]]:
    visitor_types: list[type[ErrorVisitor]] = [RulesOfHooksVisitor]
    if exhaustive_hook_deps:
        visitor_types.append(ExhaustiveDepsVisitor)

    errors: list[tuple[int, int, str]] = []
    for vtype in visitor_types:
        visitor = vtype()
        visitor.visit(tree)
        errors.extend(visitor.errors)

    return errors
