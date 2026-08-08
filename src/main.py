"""Command-line entry point for the Mini-language compiler frontend."""

import argparse
from pathlib import Path

from antlr4 import CommonTokenStream, InputStream
from antlr4.Token import Token

from src.ast.printer import format_ast
from src.codegen.tac_generator import TacGenerator
from src.lexer.MiniLexer import MiniLexer
from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


def format_tokens(source: str) -> str:
    """Return lexer tokens in source order for CLI diagnostics."""
    lexer = MiniLexer(InputStream(source))
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()
    lines = ["Tokens:"]
    for token in token_stream.tokens:
        if token.type == Token.EOF:
            continue
        token_type = lexer.symbolicNames[token.type]
        lines.append(f"  {token_type}: {token.text!r} (line {token.line})")
    return "\n".join(lines)


def format_symbol_table(analyzer: SemanticAnalyzer) -> str:
    """Return active and completed scopes without affecting compilation."""
    lines = ["Symbol table:"]
    for depth, entries in enumerate(analyzer.symbol_table.active_scopes):
        lines.append(f"  Active scope {depth}:")
        lines.extend(_format_entries(entries))
    for index, snapshot in enumerate(analyzer.symbol_table.scope_history, start=1):
        lines.append(f"  Closed scope {snapshot.depth} (exit #{index}):")
        lines.extend(_format_entries(snapshot.entries))
    return "\n".join(lines)


def _format_entries(entries) -> list[str]:
    if not entries:
        return ["    <empty>"]
    return [
        f"    {entry.name}: type={entry.var_type}, scope={entry.scope_level}, "
        f"declared_line={entry.declared_line}"
        for entry in entries
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and semantically validate a Mini program.")
    parser.add_argument("file", type=Path, help="Path to a .mini source file")
    parser.add_argument("--ast", action="store_true", help="Print the AST after successful parsing")
    parser.add_argument("--tac", action="store_true", help="Print three-address code after semantic analysis")
    parser.add_argument("--tokens", action="store_true", help="Print lexer tokens before parsing")
    parser.add_argument("--symtable", action="store_true", help="Print symbol-table scopes after semantic analysis")
    args = parser.parse_args()

    try:
        source = args.file.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(str(error))

    if args.tokens:
        print(format_tokens(source))

    try:
        program = parse_source_to_ast(source)
    except SyntaxError as error:
        print(f"Syntax error: {error}")
        return 1

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(program)
    if args.symtable:
        print(format_symbol_table(analyzer))
    if errors:
        for error in errors:
            print(f"Semantic error [{error.rule}] line {error.line}: {error.message}")
        return 1
    if args.tac:
        print("\n".join(TacGenerator().generate(program)))
    if args.ast:
        print(format_ast(program))
    print("Compilation succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
