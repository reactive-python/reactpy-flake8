import ast
from contextlib import contextmanager
from typing import List, Tuple, Iterator, Any


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
    return is_component_function_name(node.name)


def is_component_function_name(name: str) -> bool:
    return name[0].upper() == name[0] and "_" not in name


def is_hook_function_name(name: str) -> bool:
    return name.lstrip("_").startswith("use_")
