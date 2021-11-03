import ast
from contextlib import contextmanager
from typing import Any, Iterator, List, Tuple


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
    return any(
        decorator.value.id == "idom" and decorator.attr == "component"
        for decorator in node.decorator_list
    )


def is_hook_function_name(name: str) -> bool:
    return name.lstrip("_").startswith("use_")
