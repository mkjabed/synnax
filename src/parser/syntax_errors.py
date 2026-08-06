from antlr4.error.ErrorListener import ErrorListener


class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"line {line}:{column} {msg}")

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)
