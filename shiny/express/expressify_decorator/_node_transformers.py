from __future__ import annotations

import ast
import types
from typing import Any, Callable, cast

from ._helpers import ast_matches_func

sys_alias = "__auto_displayhook_sys__"
expressify_decorator_func_name = "_expressify_decorator_function_def"
session_context_func_name = "__shiny_session_context__"


class TopLevelTransformer(ast.NodeTransformer):
    def generic_visit(self, node: ast.AST) -> ast.AST:
        return node

    def descend(self, node: ast.AST) -> object:
        return super().generic_visit(node)

    # These are all node types we need to descend into. Any nodes not explicitly
    # sent to super().generic_visit() will go to self.generic_visit(), i.e. the
    # node and its descendants will be left unchanged.

    def visit_Module(self, node: ast.Module) -> object:
        return self.descend(node)

    def visit_With(self, node: ast.With) -> object:
        return self.descend(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> object:
        return self.descend(node)

    def visit_If(self, node: ast.If) -> object:
        return self.descend(node)

    def visit_IfExp(self, node: ast.IfExp) -> object:
        return self.descend(node)

    def visit_For(self, node: ast.For) -> object:
        return self.descend(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> object:
        return self.descend(node)

    def visit_While(self, node: ast.While) -> object:
        return self.descend(node)

    def visit_Try(self, node: ast.Try) -> object:
        return self.descend(node)


class FuncBodyDisplayHookTransformer(TopLevelTransformer):
    """
    A NodeTransformer that wraps expressions in a function body's top level and
    within specific flow control statements with sys.displayhook calls, without
    affecting inner functions.

    The NodeTransformer is indiscriminate in what it wraps--the first
    FunctionDef it finds will be transformed.
    """

    def __init__(self):
        self.saw_func = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> object:
        """
        Descend into the first (and ONLY the first) function we find.
        """
        if self.saw_func:
            return node

        self.saw_func = True
        return self.descend(node)

    def visit_Expr(self, node: ast.Expr) -> object:
        """
        Each expr we come across will be wrapped in a call to sys.displayhook.
        Note that we don't descend into the node, so child expressions will not
        be affected.
        """
        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id=sys_alias, ctx=ast.Load()),
                args=[node.value],
                keywords=[],
            )
        )


class TargetFunctionTransformer(ast.NodeTransformer):
    """
    Find the first FunctionDef that matches a target function, and transform it
    using a given function.
    """

    def __init__(
        self, target: types.FunctionType, transform: Callable[[ast.AST], ast.AST]
    ):
        self.target = target
        self.transform = transform
        self.found: ast.FunctionDef | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if not self.found and ast_matches_func(node, self.target):
            self.found = node
            new_node = self.transform(node)
            self.found = cast(ast.FunctionDef, new_node)
            return new_node
        else:
            return self.generic_visit(node)


class DisplayFuncsTransformer(TopLevelTransformer):
    # Visit top-level functions and async functions, inserting @sys.displayhook at the
    # top of their decorator lists

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.decorator_list.insert(
            0, ast.Name(id=expressify_decorator_func_name, ctx=ast.Load())
        )
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> object:
        node.decorator_list.insert(
            0, ast.Name(id=expressify_decorator_func_name, ctx=ast.Load())
        )
        return node


class ImportSharedSessionContextTransformer(TopLevelTransformer):
    def __init__(self, module_name: str):
        self.module_name = module_name

    def visit_Import(self, node: ast.Import) -> ast.AST:
        if any(alias.name == self.module_name for alias in node.names):
            return self._create_with_block(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module == self.module_name:
            return self._create_with_block(node)
        return node

    def _create_with_block(self, original_node: ast.Import | ast.ImportFrom):
        with_node = ast.With()
        with_node.items = [
            ast.withitem(
                context_expr=ast.Call(
                    func=ast.Name(id=session_context_func_name, ctx=ast.Load()),
                    args=[ast.Constant(value=None)],
                    keywords=[],
                ),
                optional_vars=None,
            )
        ]
        with_node.body = [original_node]
        return with_node
