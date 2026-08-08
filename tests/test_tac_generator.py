from src.codegen.tac_generator import TacGenerator
from src.parser.parse import parse_source_to_ast


def generate(source: str) -> list[str]:
    return TacGenerator().generate(parse_source_to_ast(source))


def test_generates_tac_for_arithmetic_assignment_and_print():
    lines = generate("int x; int a; int b; x = a + b * 2; print x;")
    assert lines == ["t1 = b * 2", "t2 = a + t1", "x = t2", "print x"]


def test_generates_tac_for_relational_logical_and_unary_expressions():
    lines = generate("bool result; bool flag; int x; result = !flag || x > 0;")
    assert lines == ["t1 = !flag", "t2 = x > 0", "t3 = t1 || t2", "result = t3"]


def test_literals_and_plain_blocks_need_no_extra_instructions():
    lines = generate("bool ok; { ok = true; print false; }")
    assert lines == ["ok = true", "print false"]


def test_generates_tac_for_if_without_else():
    lines = generate("bool ok; int x; if (ok) { x = 1; } print x;")
    assert lines == ["ifFalse ok goto L1", "x = 1", "L1:", "print x"]


def test_generates_tac_for_if_else():
    lines = generate("bool ok; int x; if (ok) { x = 1; } else { x = 2; }")
    assert lines == [
        "ifFalse ok goto L1", "x = 1", "goto L2", "L1:", "x = 2", "L2:"
    ]


def test_generates_tac_for_while_with_expression_condition():
    lines = generate("int x; while (x > 0) { x = x - 1; }")
    assert lines == [
        "L1:", "t1 = x > 0", "ifFalse t1 goto L2", "t2 = x - 1",
        "x = t2", "goto L1", "L2:"
    ]


def test_labels_are_unique_for_nested_control_flow():
    lines = generate("bool a; bool b; while (a) { if (b) { print b; } }")
    assert lines == [
        "L1:", "ifFalse a goto L2", "ifFalse b goto L3", "print b", "L3:",
        "goto L1", "L2:"
    ]
