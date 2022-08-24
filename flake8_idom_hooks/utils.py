import ast
import re
from contextlib import contextmanager
from typing import Any, Iterator, List, Tuple

_COMPONENT_DECORATOR_NAME_PATTERN = re.compile(r"^(idom.(\w+\.)*)?component$")


@contextmanager
def set_current(obj: Any, **attrs: Any) -> Iterator[None]:
    old_attrs = {k: getattr(obj, f"_current_{k}") for k in attrs}
    for k, v in attrs.items():
        setattr(obj, f"_current_{k}", v)
    try:
        yield
    finally:
        for k, v in old_attrs.items():
            setattr(obj, f"_current_{k}", v)


class ErrorVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

    def _save_error(self, error_code: int, node: ast.AST, message: str) -> None:
        self.errors.append((node.lineno, node.col_offset, f"ROH{error_code} {message}"))


def is_hook_def(node: ast.FunctionDef) -> bool:
    return is_hook_function_name(node.name)


def is_component_def(node: ast.FunctionDef) -> bool:
    return any(map(_is_component_decorator, node.decorator_list))


def is_hook_function_name(name: str) -> bool:
    return name.lstrip("_").startswith("use_")


def _is_component_decorator(node: ast.AST) -> bool:
    return (
        _COMPONENT_DECORATOR_NAME_PATTERN.match(
            ".".join(reversed(list(_get_dotted_name(node))))
        )
        is not None
    )


def _get_dotted_name(node: ast.AST) -> Iterator[str]:
    while isinstance(node, ast.Attribute):
        yield node.attr
        node = node.value
    if isinstance(node, ast.Name):
        yield node.id
