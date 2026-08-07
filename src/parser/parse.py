from antlr4 import CommonTokenStream, InputStream

from src.ast.builder import AstBuilder
from src.lexer.MiniLexer import MiniLexer
from src.parser.MiniParser import MiniParser
from src.parser.syntax_errors import SyntaxErrorListener


def parse_source_to_ast(source: str):
    input_stream = InputStream(source)
    lexer = MiniLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = MiniParser(token_stream)

    syntax_listener = SyntaxErrorListener()
    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    lexer.addErrorListener(syntax_listener)
    parser.addErrorListener(syntax_listener)

    tree = parser.program()
    if syntax_listener.has_errors:
        raise SyntaxError("\n".join(syntax_listener.errors))

    return AstBuilder().visit(tree)
