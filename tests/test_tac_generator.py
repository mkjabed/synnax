import pytest

from src.codegen.tac_generator import TacGenerationError, TacGenerator
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


def test_control_flow_is_rejected_until_day_8():
    program = parse_source_to_ast("bool ok; if (ok) { print ok; }")
    with pytest.raises(TacGenerationError, match="Day 8"):
        TacGenerator().generate(program)
