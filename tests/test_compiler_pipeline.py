"""End-to-end regression tests for the nine required Mini programs."""

from pathlib import Path

import pytest

from src.codegen.tac_generator import TacGenerator
from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


TESTS = Path(__file__).parent


def read_program(*parts: str) -> str:
    return (TESTS.joinpath(*parts)).read_text(encoding="utf-8")


def test_valid_program_reaches_expected_tac():
    program = parse_source_to_ast(read_program("valid", "valid_program.mini"))
    assert SemanticAnalyzer().analyze(program) == []

    actual = "\n".join(TacGenerator().generate(program)) + "\n"
    expected = read_program("valid", "valid_program.tac")
    assert actual == expected


def test_lexical_error_program_reports_line_number():
    with pytest.raises(SyntaxError, match=r"line 6:6 token recognition error"):
        parse_source_to_ast(read_program("lexical_errors", "invalid_character.mini"))


def test_syntax_error_program_recovers_and_reports_both_errors():
    with pytest.raises(SyntaxError) as error:
        parse_source_to_ast(read_program("syntax_errors", "missing_tokens.mini"))

    message = str(error.value)
    assert "line 11:0 missing ';'" in message
    assert "line 13:13 missing ')'" in message


@pytest.mark.parametrize(
    ("filename", "expected_rule"),
    [
        ("undeclared_variable.mini", "undeclared_variable"),
        ("redeclaration.mini", "redeclaration"),
        ("scope_violation.mini", "scope_violation"),
        ("type_mismatch.mini", "type_mismatch"),
        ("invalid_assignment.mini", "invalid_assignment"),
        ("invalid_expression.mini", "invalid_expression"),
    ],
)
def test_each_required_semantic_error_program_reports_its_rule(filename, expected_rule):
    program = parse_source_to_ast(read_program("semantic_errors", filename))
    errors = SemanticAnalyzer().analyze(program)
    assert [error.rule for error in errors] == [expected_rule]
