from __future__ import annotations

import ast

from .common import CheckContext
from .exhaustive_deps import ExhaustiveDepsVisitor
from .rules_of_hooks import RulesOfHooksVisitor

DEFAULT_COMPONENT_DECORATOR_PATTERN = r"^(component|[\w\.]+\.component)$"
DEFAULT_HOOK_FUNCTION_PATTERN = r"^_*use_\w+$"


def run_checks(
    tree: ast.Module,
    exhaustive_hook_deps: bool,
    component_decorator_pattern: str = DEFAULT_COMPONENT_DECORATOR_PATTERN,
    hook_function_pattern: str = DEFAULT_HOOK_FUNCTION_PATTERN,
) -> list[tuple[int, int, str]]:
    context = CheckContext(component_decorator_pattern, hook_function_pattern)

    visitors: list[ast.NodeVisitor] = [RulesOfHooksVisitor(context)]
    if exhaustive_hook_deps:
        visitors.append(ExhaustiveDepsVisitor(context))

    for v in visitors:
        v.visit(tree)

    return context.errors
