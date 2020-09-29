import ast
from typing import List, Tuple


class ErrorVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

    def _save_error(self, error_code: int, node: ast.AST, message: str) -> None:
        self.errors.append((node.lineno, node.col_offset, f"ROH{error_code} {message}"))


def is_hook_def(node: ast.FunctionDef) -> bool:
    return is_hook_function_name(node.name)


def is_element_def(node: ast.FunctionDef) -> bool:
    return is_element_function_name(node.name)


def is_element_function_name(name: str) -> bool:
    return name[0].upper() == name[0] and "_" not in name


def is_hook_function_name(name: str) -> bool:
    return name.lstrip("_").startswith("use_")
