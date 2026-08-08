"""Generate three-address code (TAC) for expressions and simple statements."""

from src.ast.nodes import (
    AssignNode, BinaryOpNode, BlockNode, BoolLiteralNode, Expr,
    FloatLiteralNode, IdentifierNode, IntLiteralNode, PrintNode, ProgramNode,
    Stmt, UnaryNotNode, VarDeclNode,
)


class TacGenerationError(Exception):
    """Raised when a construct scheduled for a later TAC milestone is used."""


class TacGenerator:
    """Lower a semantically valid AST into readable three-address code.

    Day 7 covers expressions, assignments, print statements, and plain
    blocks. Branching and loop control flow deliberately wait for Day 8.
    """

    def __init__(self):
        self._lines: list[str] = []
        self._temporary_count = 0

    def generate(self, program: ProgramNode) -> list[str]:
        self._lines = []
        self._temporary_count = 0
        for statement in program.statements:
            self._emit_statement(statement)
        return self._lines.copy()

    def _emit_statement(self, statement: Stmt) -> None:
        match statement:
            case VarDeclNode():
                # Declarations affect semantic analysis but require no runtime
                # TAC instruction in this untyped intermediate representation.
                return
            case AssignNode(name=name, value=value):
                self._lines.append(f"{name} = {self._emit_expression(value)}")
            case PrintNode(value=value):
                self._lines.append(f"print {self._emit_expression(value)}")
            case BlockNode(statements=statements):
                for nested_statement in statements:
                    self._emit_statement(nested_statement)
            case _:
                raise TacGenerationError(
                    f"TAC for {type(statement).__name__} is scheduled for Day 8"
                )

    def _emit_expression(self, expression: Expr) -> str:
        match expression:
            case IdentifierNode(name=name):
                return name
            case IntLiteralNode(value=value):
                return str(value)
            case FloatLiteralNode(value=value):
                return str(value)
            case BoolLiteralNode(value=value):
                return "true" if value else "false"
            case UnaryNotNode(operand=operand):
                temporary = self._new_temporary()
                self._lines.append(f"{temporary} = !{self._emit_expression(operand)}")
                return temporary
            case BinaryOpNode(left=left, op=operator, right=right):
                left_value = self._emit_expression(left)
                right_value = self._emit_expression(right)
                temporary = self._new_temporary()
                self._lines.append(f"{temporary} = {left_value} {operator} {right_value}")
                return temporary
            case _:
                raise TypeError(f"Unhandled expression node: {type(expression).__name__}")

    def _new_temporary(self) -> str:
        self._temporary_count += 1
        return f"t{self._temporary_count}"
