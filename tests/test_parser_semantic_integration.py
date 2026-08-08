from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


def analyze_source(source: str):
    program = parse_source_to_ast(source)
    return SemanticAnalyzer().analyze(program) # type: ignore


def test_valid_source_from_real_parser_reports_no_semantic_errors():
    errors = analyze_source(
        """
        int x;
        x = 5;

        if (x > 0) {
            int inner;
            inner = x + 1;
            print inner;
        } else {
            print x;
        }

        while (x > 0) {
            x = x - 1;
        }
        """
    )

    assert errors == []


def test_undeclared_variable_from_real_parser_is_reported():
    errors = analyze_source(
        """
        int x;
        x = 5;
        print y;
        """
    )

    assert len(errors) == 1
    assert errors[0].rule == "undeclared_variable"
    assert errors[0].line == 4
