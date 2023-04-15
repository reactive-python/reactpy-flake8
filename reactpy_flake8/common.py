from __future__ import annotations

import ast
import re
from contextlib import contextmanager
from typing import Any, Iterator


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


class CheckContext:
    def __init__(
        self, component_decorator_pattern: str, hook_function_pattern: str
    ) -> None:
        self.errors: list[tuple[int, int, str]] = []
        self._hook_function_pattern = re.compile(hook_function_pattern)
        self._component_decorator_pattern = re.compile(component_decorator_pattern)

    def add_error(self, error_code: int, node: ast.AST, message: str) -> None:
        self.errors.append((node.lineno, node.col_offset, f"ROH{error_code} {message}"))

    def is_hook_def(self, node: ast.FunctionDef) -> bool:
        return self.is_hook_name(node.name)

    def is_hook_name(self, name: str) -> bool:
        return self._hook_function_pattern.match(name) is not None

    def is_component_def(self, node: ast.FunctionDef) -> bool:
        return any(map(self.is_component_decorator, node.decorator_list))

    def is_component_decorator(self, node: ast.AST) -> bool:
        deco_name_parts: list[str] = []
        while isinstance(node, ast.Attribute):
            deco_name_parts.insert(0, node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            deco_name_parts.insert(0, node.id)
        return (
            self._component_decorator_pattern.match(".".join(deco_name_parts))
            is not None
        )
