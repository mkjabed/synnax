"""Command-line entry point for the Mini-language compiler frontend."""

import argparse
from pathlib import Path

from src.ast.printer import format_ast
from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and semantically validate a Mini program.")
    parser.add_argument("file", type=Path, help="Path to a .mini source file")
    parser.add_argument("--ast", action="store_true", help="Print the AST after successful parsing")
    args = parser.parse_args()

    try:
        program = parse_source_to_ast(args.file.read_text(encoding="utf-8"))
    except OSError as error:
        parser.error(str(error))
    except SyntaxError as error:
        print(f"Syntax error: {error}")
        return 1

    errors = SemanticAnalyzer().analyze(program)
    if errors:
        for error in errors:
            print(f"Semantic error [{error.rule}] line {error.line}: {error.message}")
        return 1
    if args.ast:
        print(format_ast(program))
    print("Compilation succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
