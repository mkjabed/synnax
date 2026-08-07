from src.ast.nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    PrintNode,
    ProgramNode,
    UnaryNotNode,
    VarDeclNode,
    WhileNode,
)


def format_ast(node) -> str:
    return "\n".join(_format_node(node, indent=0))


def _format_node(node, indent: int) -> list[str]:
    pad = "  " * indent

    match node:
        case ProgramNode(statements=statements):
            lines = [f"{pad}Program"]
            lines.extend(_format_statement_list(statements, indent + 1))
            return lines
        case VarDeclNode(var_type=var_type, name=name, line=line):
            return [f"{pad}VarDecl(type={var_type}, name={name}, line={line})"]
        case AssignNode(name=name, value=value, line=line):
            lines = [f"{pad}Assign(name={name}, line={line})"]
            lines.extend(_format_node(value, indent + 1))
            return lines
        case PrintNode(value=value, line=line):
            lines = [f"{pad}Print(line={line})"]
            lines.extend(_format_node(value, indent + 1))
            return lines
        case BlockNode(statements=statements, line=line):
            lines = [f"{pad}Block(line={line})"]
            lines.extend(_format_statement_list(statements, indent + 1))
            return lines
        case IfNode(condition=condition, then_block=then_block, else_block=else_block, line=line):
            lines = [f"{pad}If(line={line})", f"{pad}  Condition:"]
            lines.extend(_format_node(condition, indent + 2))
            lines.append(f"{pad}  Then:")
            lines.extend(_format_node(then_block, indent + 2))
            if else_block is not None:
                lines.append(f"{pad}  Else:")
                lines.extend(_format_node(else_block, indent + 2))
            return lines
        case WhileNode(condition=condition, body=body, line=line):
            lines = [f"{pad}While(line={line})", f"{pad}  Condition:"]
            lines.extend(_format_node(condition, indent + 2))
            lines.append(f"{pad}  Body:")
            lines.extend(_format_node(body, indent + 2))
            return lines
        case BinaryOpNode(op=op, left=left, right=right, line=line):
            lines = [f"{pad}BinaryOp(op={op}, line={line})"]
            lines.extend(_format_node(left, indent + 1))
            lines.extend(_format_node(right, indent + 1))
            return lines
        case UnaryNotNode(operand=operand, line=line):
            lines = [f"{pad}UnaryNot(line={line})"]
            lines.extend(_format_node(operand, indent + 1))
            return lines
        case IdentifierNode(name=name, line=line):
            return [f"{pad}Identifier(name={name}, line={line})"]
        case IntLiteralNode(value=value, line=line):
            return [f"{pad}IntLiteral(value={value}, line={line})"]
        case FloatLiteralNode(value=value, line=line):
            return [f"{pad}FloatLiteral(value={value}, line={line})"]
        case BoolLiteralNode(value=value, line=line):
            return [f"{pad}BoolLiteral(value={value}, line={line})"]
        case _:
            raise TypeError(f"Unhandled AST node: {type(node).__name__}")


def _format_statement_list(statements, indent: int) -> list[str]:
    lines: list[str] = []
    for stmt in statements:
        lines.extend(_format_node(stmt, indent))
    return lines
