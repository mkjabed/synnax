"""
src/semantic/semantic_analyzer.py — rules 1-3 of Section 4.5.

Implements: undeclared variable use, redeclaration, scope violation.
Rules 4-6 (type mismatch, invalid assignment, invalid expression) are
deliberately NOT implemented yet — that's Day 6's work, once type
information can actually be threaded through expressions. Calling
_visit_assign / _visit_expr here does NOT check types; it only checks
that names exist and are in scope.

Walks the AST using structural pattern matching (`match`) rather than
a classic visitor-pattern accept()/visit() pair, since the AST nodes in
src/ast/nodes.py are plain dataclasses with no behavior of their own —
match on type is simpler here and equally explicit.
"""

from src.ast.nodes import (
    ProgramNode, Stmt, Expr,
    VarDeclNode, AssignNode, PrintNode, BlockNode, IfNode, WhileNode,
    BinaryOpNode, UnaryNotNode, IdentifierNode,
    IntLiteralNode, FloatLiteralNode, BoolLiteralNode,
)
from src.symbol_table.symbol_table import SymbolTable, RedeclarationError
from src.semantic.errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[SemanticError] = []

        # Names declared ANYWHERE in the program, ever — never removed,
        # even after their scope exits. This is what lets us tell apart
        # two errors that would otherwise look identical to a plain
        # SymbolTable.lookup() failure:
        #   - rule 1 (undeclared variable): name never appears here
        #   - rule 3 (scope violation): name DOES appear here, but the
        #     current lookup still failed, meaning its block has closed
        self._ever_declared: set[str] = set()

    def analyze(self, program: ProgramNode) -> list[SemanticError]:
        for stmt in program.statements:
            self._visit_stmt(stmt)
        return self.errors

    # ---------------- statements ----------------

    def _visit_stmt(self, stmt: Stmt) -> None:
        match stmt:
            case VarDeclNode():
                self._visit_var_decl(stmt)
            case AssignNode():
                self._visit_assign(stmt)
            case PrintNode():
                self._visit_print(stmt)
            case BlockNode():
                self._visit_block(stmt)
            case IfNode():
                self._visit_if(stmt)
            case WhileNode():
                self._visit_while(stmt)
            case _:
                raise TypeError(f"Unhandled statement node: {type(stmt).__name__}")

    def _visit_var_decl(self, node: VarDeclNode) -> None:
        try:
            self.symbol_table.declare(node.name, node.var_type, node.line)
            self._ever_declared.add(node.name)
        except RedeclarationError as e:
            self.errors.append(SemanticError(
                line=node.line,
                rule="redeclaration",
                message=str(e),
            ))

    def _visit_assign(self, node: AssignNode) -> None:
        self._check_name_usage(node.name, node.line)
        self._visit_expr(node.value)
        # Type-checking the assignment itself (rules 4-6) is Day 6's job.

    def _visit_print(self, node: PrintNode) -> None:
        self._visit_expr(node.value)

    def _visit_block(self, node: BlockNode) -> None:
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self._visit_stmt(stmt)
        self.symbol_table.exit_scope()

    def _visit_if(self, node: IfNode) -> None:
        self._visit_expr(node.condition)
        self._visit_block(node.then_block)
        if node.else_block is not None:
            self._visit_block(node.else_block)

    def _visit_while(self, node: WhileNode) -> None:
        self._visit_expr(node.condition)
        self._visit_block(node.body)

    # ---------------- expressions ----------------

    def _visit_expr(self, expr: Expr) -> None:
        match expr:
            case IdentifierNode():
                self._check_name_usage(expr.name, expr.line)
            case BinaryOpNode():
                self._visit_expr(expr.left)
                self._visit_expr(expr.right)
            case UnaryNotNode():
                self._visit_expr(expr.operand)
            case IntLiteralNode() | FloatLiteralNode() | BoolLiteralNode():
                pass  # literals never reference a name — nothing to check
            case _:
                raise TypeError(f"Unhandled expression node: {type(expr).__name__}")

    # ---------------- shared lookup/reporting ----------------

    def _check_name_usage(self, name: str, line: int) -> None:
        if self.symbol_table.lookup(name) is not None:
            return  # declared and currently in an active scope — fine

        if name in self._ever_declared:
            self.errors.append(SemanticError(
                line=line,
                rule="scope_violation",
                message=(
                    f"'{name}' used at line {line} is out of scope here "
                    f"(it was declared earlier, but its block has already closed)"
                ),
            ))
        else:
            self.errors.append(SemanticError(
                line=line,
                rule="undeclared_variable",
                message=f"'{name}' used at line {line} was never declared",
            ))
