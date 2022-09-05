import ast
from typing import Optional, Union

from .common import CheckContext, set_current


class RulesOfHooksVisitor(ast.NodeVisitor):
    def __init__(self, context: CheckContext) -> None:
        self._context = context
        self._current_hook: Optional[ast.FunctionDef] = None
        self._current_component: Optional[ast.FunctionDef] = None
        self._current_function: Optional[ast.FunctionDef] = None
        self._current_call: Optional[ast.Call] = None
        self._current_conditional: Union[None, ast.If, ast.IfExp, ast.Try] = None
        self._current_loop: Union[None, ast.For, ast.While] = None

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
            ):
                self.generic_visit(node)
        else:
            with set_current(self, function=node):
                self.generic_visit(node)

    def _visit_hook_usage(self, node: Union[ast.Name, ast.Attribute]) -> None:
        self._check_if_propper_hook_usage(node)

    visit_Attribute = _visit_hook_usage
    visit_Name = _visit_hook_usage

    def _visit_conditional(self, node: ast.AST) -> None:
        with set_current(self, conditional=node):
            self.generic_visit(node)

    visit_If = _visit_conditional
    visit_IfExp = _visit_conditional
    visit_Try = _visit_conditional

    def _visit_loop(self, node: ast.AST) -> None:
        with set_current(self, loop=node):
            self.generic_visit(node)

    visit_For = _visit_loop
    visit_While = _visit_loop

    def _check_if_hook_defined_in_function(self, node: ast.FunctionDef) -> None:
        if self._current_function is not None:
            msg = f"hook {node.name!r} defined as closure in function {self._current_function.name!r}"
            self._context.add_error(100, node, msg)

    def _check_if_propper_hook_usage(
        self, node: Union[ast.Name, ast.Attribute]
    ) -> None:
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
            node_type = type(loop_or_conditional)
            node_type_to_name = {
                ast.If: "if statement",
                ast.IfExp: "inline if expression",
                ast.Try: "try statement",
                ast.For: "for loop",
                ast.While: "while loop",
            }
            node_name = node_type_to_name[node_type]
            msg = f"hook {name!r} used inside {node_name}"
            self._context.add_error(102, node, msg)
