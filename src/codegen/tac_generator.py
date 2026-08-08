"""Generate three-address code (TAC) for Mini-language programs."""

from src.ast.nodes import (
    AssignNode, BinaryOpNode, BlockNode, BoolLiteralNode, Expr,
    FloatLiteralNode, IdentifierNode, IntLiteralNode, PrintNode, ProgramNode,
    IfNode, Stmt, UnaryNotNode, VarDeclNode, WhileNode,
)


class TacGenerator:
    """Lower a semantically valid AST into readable three-address code.

    Expressions are evaluated into deterministic temporary variables. Control
    flow uses labels and ``ifFalse`` jumps, allowing generated TAC to be
    hand-traced directly.
    """

    def __init__(self):
        self._lines: list[str] = []
        self._temporary_count = 0
        self._label_count = 0

    def generate(self, program: ProgramNode) -> list[str]:
        self._lines = []
        self._temporary_count = 0
        self._label_count = 0
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
            case IfNode():
                self._emit_if(statement)
            case WhileNode():
                self._emit_while(statement)
            case _:
                raise TypeError(f"Unhandled statement node: {type(statement).__name__}")

    def _emit_if(self, node: IfNode) -> None:
        condition = self._emit_expression(node.condition)
        false_label = self._new_label()
        self._lines.append(f"ifFalse {condition} goto {false_label}")
        self._emit_statement(node.then_block)

        if node.else_block is None:
            self._lines.append(f"{false_label}:")
            return

        end_label = self._new_label()
        self._lines.append(f"goto {end_label}")
        self._lines.append(f"{false_label}:")
        self._emit_statement(node.else_block)
        self._lines.append(f"{end_label}:")

    def _emit_while(self, node: WhileNode) -> None:
        start_label = self._new_label()
        exit_label = self._new_label()
        self._lines.append(f"{start_label}:")
        condition = self._emit_expression(node.condition)
        self._lines.append(f"ifFalse {condition} goto {exit_label}")
        self._emit_statement(node.body)
        self._lines.append(f"goto {start_label}")
        self._lines.append(f"{exit_label}:")

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

    def _new_label(self) -> str:
        self._label_count += 1
        return f"L{self._label_count}"
