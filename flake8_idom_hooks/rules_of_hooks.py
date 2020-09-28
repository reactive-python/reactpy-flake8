import ast
from contextlib import contextmanager
from typing import Iterator, Union, Optional, Any

from .utils import is_hook_or_element_def, ErrorVisitor, is_hook_function_name


class RulesOfHooksVisitor(ErrorVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._current_hook_or_element: Optional[ast.FunctionDef] = None
        self._current_function: Optional[ast.FunctionDef] = None
        self._current_call: Optional[ast.Call] = None
        self._current_conditional: Union[None, ast.If, ast.IfExp, ast.Try] = None
        self._current_loop: Union[None, ast.For, ast.While] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if is_hook_or_element_def(node):
            self._check_if_hook_defined_in_function(node)
            with self._set_current(hook_or_element=node, function=node):
                self.generic_visit(node)
        else:
            with self._set_current(function=node):
                self.generic_visit(node)

    def _visit_hook_usage(self, node: Union[ast.Name, ast.Attribute]) -> None:
        self._check_if_propper_hook_usage(node)

    visit_Attribute = _visit_hook_usage
    visit_Name = _visit_hook_usage

    def _visit_conditional(self, node: ast.AST) -> None:
        with self._set_current(conditional=node):
            self.generic_visit(node)

    visit_If = _visit_conditional
    visit_IfExp = _visit_conditional
    visit_Try = _visit_conditional

    def _visit_loop(self, node: ast.AST) -> None:
        with self._set_current(loop=node):
            self.generic_visit(node)

    visit_For = _visit_loop
    visit_While = _visit_loop

    def _check_if_hook_defined_in_function(self, node: ast.FunctionDef) -> None:
        if self._current_function is not None:
            msg = f"hook {node.name!r} defined as closure in function {self._current_function.name!r}"
            self._save_error(100, node, msg)

    def _check_if_propper_hook_usage(
        self, node: Union[ast.Name, ast.Attribute]
    ) -> None:
        if isinstance(node, ast.Name):
            name = node.id
        else:
            name = node.attr

        if not is_hook_function_name(name):
            return None

        if self._current_hook_or_element is None:
            msg = f"hook {name!r} used outside element or hook definition"
            self._save_error(101, node, msg)

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
            self._save_error(102, node, msg)

    @contextmanager
    def _set_current(self, **attrs: Any) -> Iterator[None]:
        old_attrs = {k: getattr(self, f"_current_{k}") for k in attrs}
        for k, v in attrs.items():
            setattr(self, f"_current_{k}", v)
        try:
            yield
        finally:
            for k, v in old_attrs.items():
                setattr(self, f"_current_{k}", v)
