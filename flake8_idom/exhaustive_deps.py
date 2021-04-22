import ast
from typing import Optional, Union, Set

from .utils import is_hook_def, is_component_def, ErrorVisitor, set_current


HOOKS_WITH_DEPS = ("use_effect", "use_callback", "use_memo")


class ExhaustiveDepsVisitor(ErrorVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._current_function: Optional[ast.FunctionDef] = None
        self._current_hook_or_component: Optional[ast.FunctionDef] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if is_hook_def(node) or is_component_def(node):
            with set_current(self, hook_or_component=node):
                self.generic_visit(node)
        elif self._current_hook_or_component is not None:
            for deco in node.decorator_list:
                if not isinstance(deco, ast.Call):
                    continue

                called_func = deco.func
                if isinstance(called_func, ast.Name):
                    called_func_name = called_func.id
                elif isinstance(called_func, ast.Attribute):
                    called_func_name = called_func.attr
                else:  # pragma: no cover
                    continue

                if called_func_name not in HOOKS_WITH_DEPS:
                    continue

                for kw in deco.keywords:
                    if kw.arg == "args":
                        self._check_hook_dependency_list_is_exhaustive(
                            self._current_hook_or_component,
                            called_func_name,
                            node,
                            kw.value,
                        )
                        break

    def visit_Call(self, node: ast.Call) -> None:
        if self._current_hook_or_component is None:
            return

        called_func = node.func

        if isinstance(called_func, ast.Name):
            called_func_name = called_func.id
        elif isinstance(called_func, ast.Attribute):
            called_func_name = called_func.attr
        else:  # pragma: no cover
            return None

        if called_func_name not in HOOKS_WITH_DEPS:
            return None

        func: Optional[ast.expr] = None
        args: Optional[ast.expr] = None

        if len(node.args) == 2:
            func, args = node.args
        else:
            if len(node.args) == 1:
                func = node.args[0]
            for kw in node.keywords:
                if kw.arg == "function":
                    func = kw.value
                elif kw.arg == "args":
                    args = kw.value

        if isinstance(func, ast.Lambda):
            self._check_hook_dependency_list_is_exhaustive(
                self._current_hook_or_component,
                called_func_name,
                func,
                args,
            )

    def _check_hook_dependency_list_is_exhaustive(
        self,
        current_hook_or_component: ast.FunctionDef,
        hook_name: str,
        func: Union[ast.FunctionDef, ast.Lambda],
        dependency_expr: Optional[ast.expr],
    ) -> None:
        dep_names = self._get_dependency_names_from_expression(
            hook_name, dependency_expr
        )

        if dep_names is None:
            return None

        func_name = "lambda" if isinstance(func, ast.Lambda) else func.name

        top_level_variable_finder = _TopLevelVariableFinder()
        top_level_variable_finder.visit(current_hook_or_component)
        variables_defined_in_scope = top_level_variable_finder.variable_names

        missing_name_finder = _MissingNameFinder(
            hook_name=hook_name,
            func_name=func_name,
            dep_names=dep_names,
            names_in_scope=variables_defined_in_scope,
            ignore_names=_param_names_of_function_def(func),
        )
        if isinstance(func.body, list):
            for b in func.body:
                missing_name_finder.visit(b)
        else:
            missing_name_finder.visit(func.body)

        self.errors.extend(missing_name_finder.errors)

    def _get_dependency_names_from_expression(
        self, hook_name: str, dependency_expr: Optional[ast.expr]
    ) -> Optional[Set[str]]:
        if dependency_expr is None:
            return set()
        elif isinstance(dependency_expr, (ast.List, ast.Tuple)):
            dep_names: Set[str] = set()
            for elt in dependency_expr.elts:
                if isinstance(elt, ast.Name):
                    dep_names.add(elt.id)
                else:
                    # ideally we could deal with some common use cases, but since React's
                    # own linter doesn't do this we'll just take the easy route for now:
                    # https://github.com/facebook/react/issues/16265
                    self._save_error(
                        201,
                        elt,
                        (
                            f"dependency arg of {hook_name!r} is not destructured - "
                            "dependencies should be refered to directly, not via an "
                            "attribute or key of an object"
                        ),
                    )
            return dep_names
        else:
            self._save_error(
                202,
                dependency_expr,
                (
                    f"dependency args of {hook_name!r} should be a literal list or "
                    f"tuple - not expression type {type(dependency_expr).__name__!r}"
                ),
            )
            return None


class _MissingNameFinder(ErrorVisitor):
    def __init__(
        self,
        hook_name: str,
        func_name: str,
        dep_names: Set[str],
        ignore_names: Set[str],
        names_in_scope: Set[str],
    ) -> None:
        super().__init__()
        self._hook_name = hook_name
        self._func_name = func_name
        self._ignore_names = ignore_names
        self._dep_names = dep_names
        self._names_in_scope = names_in_scope
        self.used_deps: Set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        node_id = node.id
        if node_id not in self._ignore_names and node_id in self._names_in_scope:
            if node_id in self._dep_names:
                self.used_deps.add(node_id)
            else:
                self._save_error(
                    203,
                    node,
                    (
                        f"dependency {node_id!r} of function {self._func_name!r} "
                        f"is not specified in declaration of {self._hook_name!r}"
                    ),
                )


class _TopLevelVariableFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self._scope_entered = False
        self._current_scope_is_top_level = True
        self.variable_names: Set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.variable_names.add(node.id)

    def _visit_new_scope(self, node: Union[ast.FunctionDef, ast.ClassDef]) -> None:
        if not self._scope_entered:
            self._scope_entered = True
            self.generic_visit(node)
        elif self._current_scope_is_top_level:
            self.variable_names.add(node.name)

    visit_FunctionDef = _visit_new_scope
    visit_ClassDef = _visit_new_scope


def _param_names_of_function_def(func: Union[ast.FunctionDef, ast.Lambda]) -> Set[str]:
    names: Set[str] = set()
    names.update(a.arg for a in func.args.args)
    names.update(kw.arg for kw in func.args.kwonlyargs)
    if func.args.vararg is not None:
        names.add(func.args.vararg.arg)
    if func.args.kwarg is not None:
        names.add(func.args.kwarg.arg)
    return names
