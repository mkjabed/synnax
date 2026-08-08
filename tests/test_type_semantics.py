import pytest
from pathlib import Path

from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


def analyze(source: str):
    return SemanticAnalyzer().analyze(parse_source_to_ast(source))


@pytest.mark.parametrize(
    ("filename", "expected_rule"),
    [
        ("type_mismatch.mini", "type_mismatch"),
        ("invalid_assignment.mini", "invalid_assignment"),
        ("invalid_expression.mini", "invalid_expression"),
    ],
)
def test_required_semantic_error_programs(filename, expected_rule):
    source = Path("tests/semantic_errors") / filename
    errors = analyze(source.read_text(encoding="utf-8"))
    assert [error.rule for error in errors] == [expected_rule]


def test_int_to_float_assignment_is_allowed_but_float_to_int_is_not():
    errors = analyze("float f; int i; f = 1; i = 1.5;")
    assert [error.rule for error in errors] == ["type_mismatch"]


def test_operator_operands_are_type_checked():
    errors = analyze("int x; bool ok; x = 1; ok = !x;")
    assert [error.rule for error in errors] == ["invalid_expression"]


def test_valid_program_has_no_semantic_errors():
    source = Path("tests/valid/valid_program.mini").read_text(encoding="utf-8")
    assert analyze(source) == []
