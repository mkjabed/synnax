"""Semantic analysis for all six required Mini-language rules."""

from src.ast.nodes import (
    ProgramNode, Stmt, Expr, VarDeclNode, AssignNode, PrintNode, BlockNode,
    IfNode, WhileNode, BinaryOpNode, UnaryNotNode, IdentifierNode,
    IntLiteralNode, FloatLiteralNode, BoolLiteralNode,
)
from src.symbol_table.symbol_table import SymbolTable, RedeclarationError
from src.semantic.errors import SemanticError


NUMERIC_TYPES = {"int", "float"}
ARITHMETIC_OPERATORS = {"+", "-", "*", "/", "%"}
RELATIONAL_OPERATORS = {"<", ">", "<=", ">=", "==", "!="}
LOGICAL_OPERATORS = {"&&", "||"}


class SemanticAnalyzer:
    """Check declarations, scopes, assignments, and expression types.

    ``None`` is an internal unknown type. It prevents one root cause (for
    example, an undeclared identifier) from producing misleading follow-on
    type errors.
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[SemanticError] = []
        self._ever_declared: set[str] = set()

    def analyze(self, program: ProgramNode) -> list[SemanticError]:
        for stmt in program.statements:
            self._visit_stmt(stmt)
        return self.errors

    def _visit_stmt(self, stmt: Stmt) -> None:
        match stmt:
            case VarDeclNode(): self._visit_var_decl(stmt)
            case AssignNode(): self._visit_assign(stmt)
            case PrintNode(): self._infer_expr_type(stmt.value)
            case BlockNode(): self._visit_block(stmt)
            case IfNode(): self._visit_if(stmt)
            case WhileNode(): self._visit_while(stmt)
            case _: raise TypeError(f"Unhandled statement node: {type(stmt).__name__}")

    def _visit_var_decl(self, node: VarDeclNode) -> None:
        try:
            self.symbol_table.declare(node.name, node.var_type, node.line)
            self._ever_declared.add(node.name)
        except RedeclarationError as error:
            self._error(node.line, "redeclaration", str(error))

    def _visit_assign(self, node: AssignNode) -> None:
        target = self.symbol_table.lookup(node.name)
        if target is None:
            self._check_name_usage(node.name, node.line)
        value_type = self._infer_expr_type(node.value)
        if target is None or value_type is None or target.var_type == value_type:
            return

        # Widening int to float is safe and keeps ordinary mixed numeric
        # arithmetic practical; narrowing remains a type mismatch.
        if target.var_type == "float" and value_type == "int":
            return
        # Keep the two assignment diagnostics distinct as the supplied test
        # programs specify: assigning *to* bool is a type mismatch, whereas
        # assigning a boolean value into a numeric variable is an invalid
        # assignment.
        rule = "type_mismatch" if target.var_type == "bool" else "invalid_assignment" if value_type == "bool" else "type_mismatch"
        self._error(
            node.line,
            rule,
            f"cannot assign {value_type} expression to {target.var_type} variable '{node.name}'",
        )

    def _visit_block(self, node: BlockNode) -> None:
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self._visit_stmt(stmt)
        self.symbol_table.exit_scope()

    def _visit_if(self, node: IfNode) -> None:
        self._infer_expr_type(node.condition)
        self._visit_block(node.then_block)
        if node.else_block is not None:
            self._visit_block(node.else_block)

    def _visit_while(self, node: WhileNode) -> None:
        self._infer_expr_type(node.condition)
        self._visit_block(node.body)

    def _infer_expr_type(self, expr: Expr) -> str | None:
        match expr:
            case IntLiteralNode(): return "int"
            case FloatLiteralNode(): return "float"
            case BoolLiteralNode(): return "bool"
            case IdentifierNode():
                entry = self.symbol_table.lookup(expr.name)
                if entry is None:
                    self._check_name_usage(expr.name, expr.line)
                    return None
                return entry.var_type
            case UnaryNotNode():
                operand_type = self._infer_expr_type(expr.operand)
                if operand_type is not None and operand_type != "bool":
                    self._error(expr.line, "invalid_expression", f"'!' requires bool operand, got {operand_type}")
                    return None
                return "bool" if operand_type is not None else None
            case BinaryOpNode(): return self._infer_binary_type(expr)
            case _: raise TypeError(f"Unhandled expression node: {type(expr).__name__}")

    def _infer_binary_type(self, node: BinaryOpNode) -> str | None:
        left_type = self._infer_expr_type(node.left)
        right_type = self._infer_expr_type(node.right)
        if left_type is None or right_type is None:
            return None

        if node.op in ARITHMETIC_OPERATORS:
            if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                self._error(node.line, "invalid_expression", f"'{node.op}' requires numeric operands, got {left_type} and {right_type}")
                return None
            if node.op == "%" and (left_type != "int" or right_type != "int"):
                self._error(node.line, "invalid_expression", "'%' requires int operands")
                return None
            return "float" if "float" in {left_type, right_type} else "int"

        if node.op in RELATIONAL_OPERATORS:
            if node.op in {"==", "!="} and left_type == right_type:
                return "bool"
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                return "bool"
            self._error(node.line, "invalid_expression", f"'{node.op}' cannot compare {left_type} and {right_type}")
            return None

        if node.op in LOGICAL_OPERATORS:
            if left_type == right_type == "bool":
                return "bool"
            self._error(node.line, "invalid_expression", f"'{node.op}' requires bool operands, got {left_type} and {right_type}")
            return None

        raise ValueError(f"Unknown binary operator: {node.op}")

    def _check_name_usage(self, name: str, line: int) -> None:
        rule = "scope_violation" if name in self._ever_declared else "undeclared_variable"
        message = (
            f"'{name}' used at line {line} is out of scope here"
            if rule == "scope_violation" else f"'{name}' used at line {line} was never declared"
        )
        self._error(line, rule, message)

    def _error(self, line: int, rule: str, message: str) -> None:
        self.errors.append(SemanticError(line=line, rule=rule, message=message))
