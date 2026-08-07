from src.ast.nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolLiteralNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    PrintNode,
    ProgramNode,
    UnaryNotNode,
    VarDeclNode,
    WhileNode,
)
from src.parser.parse import parse_source_to_ast
from src.ast.printer import format_ast


def test_builds_statement_nodes_from_real_parse_tree():
    program = parse_source_to_ast(
        """
        int x;
        bool flag;
        x = 5;
        print x;
        """
    )

    assert isinstance(program, ProgramNode)
    assert program.statements == [
        VarDeclNode(line=2, var_type="int", name="x"),
        VarDeclNode(line=3, var_type="bool", name="flag"),
        AssignNode(line=4, name="x", value=IntLiteralNode(line=4, value=5)),
        PrintNode(line=5, value=IdentifierNode(line=5, name="x")),
    ]


def test_builds_control_flow_and_nested_blocks():
    program = parse_source_to_ast(
        """
        while (x > 0) {
            x = x - 1;
        }
        if (flag) {
            print x;
        } else {
            print 0;
        }
        """
    )

    while_node = program.statements[0]
    if_node = program.statements[1]

    assert isinstance(while_node, WhileNode)
    assert isinstance(while_node.condition, BinaryOpNode)
    assert while_node.condition.op == ">"
    assert isinstance(while_node.body, BlockNode)
    assert isinstance(while_node.body.statements[0], AssignNode)

    assert isinstance(if_node, IfNode)
    assert if_node.condition == IdentifierNode(line=5, name="flag")
    assert isinstance(if_node.then_block.statements[0], PrintNode)
    assert isinstance(if_node.else_block.statements[0], PrintNode)


def test_builds_expression_precedence_and_unary_not():
    program = parse_source_to_ast("result = !flag || x + 2 * 3 > 10;")

    expr = program.statements[0].value

    assert isinstance(expr, BinaryOpNode)
    assert expr.op == "||"
    assert isinstance(expr.left, UnaryNotNode)
    assert expr.left.operand == IdentifierNode(line=1, name="flag")

    comparison = expr.right
    assert isinstance(comparison, BinaryOpNode)
    assert comparison.op == ">"
    assert comparison.right == IntLiteralNode(line=1, value=10)

    addition = comparison.left
    assert isinstance(addition, BinaryOpNode)
    assert addition.op == "+"
    assert addition.left == IdentifierNode(line=1, name="x")

    multiplication = addition.right
    assert isinstance(multiplication, BinaryOpNode)
    assert multiplication.op == "*"
    assert multiplication.left == IntLiteralNode(line=1, value=2)
    assert multiplication.right == IntLiteralNode(line=1, value=3)


def test_syntax_errors_are_reported_before_ast_building():
    try:
        parse_source_to_ast("int x")
    except SyntaxError as exc:
        assert "line 1" in str(exc)
    else:
        raise AssertionError("Expected invalid source to raise SyntaxError")


def test_ast_printer_formats_real_ast():
    program = parse_source_to_ast("int x; x = 1 + 2;")

    assert format_ast(program) == "\n".join([
        "Program",
        "  VarDecl(type=int, name=x, line=1)",
        "  Assign(name=x, line=1)",
        "    BinaryOp(op=+, line=1)",
        "      IntLiteral(value=1, line=1)",
        "      IntLiteral(value=2, line=1)",
    ])
