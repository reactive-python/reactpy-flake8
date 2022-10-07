from __future__ import annotations

import ast
import sys

from .common import CheckContext, set_current


class RulesOfHooksVisitor(ast.NodeVisitor):
    def __init__(self, context: CheckContext) -> None:
        self._context = context
        self._current_call: ast.Call | None = None
        self._current_component: ast.FunctionDef | None = None
        self._current_conditional: ast.If | ast.IfExp | ast.Try | None = None
        self._current_early_return: ast.Return | None = None
        self._current_function: ast.FunctionDef | None = None
        self._current_hook: ast.FunctionDef | None = None
        self._current_loop: ast.For | ast.While | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._context.is_hook_def(node):
            self._check_if_hook_defined_in_function(node)
            with set_current(
                self,
                hook=node,
                function=node,
                # we need to reset these before enter new hook
                conditional=None,
                loop=None,
                early_return=None,
            ):
                self.generic_visit(node)
        elif self._context.is_component_def(node):
            with set_current(
                self,
                component=node,
                function=node,
                # we need to reset these before visiting a new component
                conditional=None,
                loop=None,
                early_return=None,
            ):
                self.generic_visit(node)
        else:
            with set_current(
                self,
                function=node,
                early_return=None,
            ):
                self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        with set_current(self, call=node):
            self.visit(node.func)
        for a in node.args:
            self.visit(a)
        for kw in node.keywords:
            self.visit(kw)

    def _visit_hook_usage(self, node: ast.Name | ast.Attribute) -> None:
        if self._current_call is not None:
            self._check_if_propper_hook_usage(node)

    visit_Attribute = _visit_hook_usage
    visit_Name = _visit_hook_usage

    def _visit_conditional(self, node: ast.AST) -> None:
        with set_current(self, conditional=node):
            self.generic_visit(node)

    visit_If = _visit_conditional
    visit_IfExp = _visit_conditional
    visit_Try = _visit_conditional
    visit_Match = _visit_conditional

    def _visit_loop(self, node: ast.AST) -> None:
        with set_current(self, loop=node):
            self.generic_visit(node)

    visit_For = _visit_loop
    visit_While = _visit_loop

    def visit_Return(self, node: ast.Return) -> None:
        if self._current_component is self._current_function:
            self._current_early_return = node

    def _check_if_hook_defined_in_function(self, node: ast.FunctionDef) -> None:
        if self._current_function is not None:
            msg = f"hook {node.name!r} defined as closure in function {self._current_function.name!r}"
            self._context.add_error(100, node, msg)

    def _check_if_propper_hook_usage(self, node: ast.Name | ast.Attribute) -> None:
        if isinstance(node, ast.Name):
            name = node.id
        else:
            name = node.attr

        if not self._context.is_hook_name(name):
            return None

        if self._current_hook is None and self._current_component is None:
            msg = f"hook {name!r} used outside component or hook definition"
            self._context.add_error(101, node, msg)

        loop_or_conditional = self._current_conditional or self._current_loop
        if loop_or_conditional is not None:
            node_name = _NODE_TYPE_TO_NAME[type(loop_or_conditional)]
            msg = f"hook {name!r} used inside {node_name}"
            self._context.add_error(102, node, msg)

        if self._current_early_return:
            self._context.add_error(
                103,
                node,
                f"hook {name!r} used after an early return on line {self._current_early_return.lineno}",
            )


_NODE_TYPE_TO_NAME = {
    ast.If: "if statement",
    ast.IfExp: "inline if expression",
    ast.Try: "try statement",
    ast.For: "for loop",
    ast.While: "while loop",
}
if sys.version_info >= (3, 10):
    _NODE_TYPE_TO_NAME[ast.Match] = "match statement"
