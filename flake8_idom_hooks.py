import ast
from contextlib import contextmanager
from pkg_resources import (
    get_distribution as _get_distribution,
    DistributionNotFound as _DistributionNotFound,
)
from typing import List, Tuple, Iterator, Union, Optional, Type


try:
    __version__ = _get_distribution(__name__).version
except _DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0"


class Plugin:

    name = __name__
    version = __version__
    options = None

    def __init__(self, tree: ast.Module):
        self._tree = tree

    def run(self) -> List[Tuple[int, int, str, Type["Plugin"]]]:
        visitor = HookRulesVisitor()
        visitor.visit(self._tree)
        cls = type(self)
        return [(line, col, msg, cls) for line, col, msg in visitor.errors]


class HookRulesVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: List[Tuple[int, int, str]] = []
        self._current_function: Optional[ast.FunctionDef] = None
        self._current_call: Optional[ast.Call] = None
        self._current_conditional: Union[None, ast.If, ast.IfExp, ast.Try] = None
        self._current_loop: Union[None, ast.For, ast.While] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_if_hook_defined_in_function(node)
        with self._set_current(function=node):
            self.generic_visit(node)

    def _visit_hook_usage(self, node: ast.AST) -> None:
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
        if self._current_function is not None and _is_hook_or_element_def(node):
            msg = f"hook {node.name!r} defined as closure in function {self._current_function.name!r}"
            self._save_error(100, node, msg)

    def _check_if_propper_hook_usage(self, node: Union[ast.Name, ast.Attribute]):
        if isinstance(node, ast.Name):
            name = node.id
        else:
            name = node.attr

        if not _is_hook_function_name(name):
            return

        if not _is_hook_or_element_def(self._current_function):
            msg = f"hook {name!r} used outside element or hook definition"
            self._save_error(101, node, msg)
            return

        _loop_or_conditional = self._current_conditional or self._current_loop
        if _loop_or_conditional is not None:
            node_type = type(_loop_or_conditional)
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
            return

    def _save_error(self, error_code: int, node: ast.AST, message: str):
        self.errors.append((node.lineno, node.col_offset, f"ROH{error_code} {message}"))

    @contextmanager
    def _set_current(self, **attrs) -> Iterator[None]:
        old_attrs = {k: getattr(self, f"_current_{k}") for k in attrs}
        for k, v in attrs.items():
            setattr(self, f"_current_{k}", v)
        try:
            yield
        finally:
            for k, v in old_attrs.items():
                setattr(self, f"_current_{k}", v)


def _is_hook_or_element_def(node: Optional[ast.FunctionDef]) -> bool:
    if node is None:
        return False
    else:
        return _is_element_function_name(node.name) or _is_hook_function_name(node.name)


def _is_element_function_name(name: str) -> bool:
    return name[0].upper() == name[0] and "_" not in name


def _is_hook_function_name(name: str) -> bool:
    return name.lstrip("_").startswith("use_")
