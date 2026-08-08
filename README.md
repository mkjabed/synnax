# Synnax

Mini-language compiler frontend built with ANTLR4 and Python. It parses source
programs, constructs an AST, and applies the six required semantic checks.

## Commands

Generate parser sources (requires the ANTLR4 command-line tool):

```sh
make generate
```

Compile a program through parsing and semantic analysis:

```sh
make run FILE=tests/valid/valid_program.mini
```

Generate TAC for programs using expressions, assignments, and `print`:

```sh
python -m src.main path/to/program.mini --tac
```

Control-flow TAC (`if` and `while`) is the Day 8 milestone.

Run the automated tests:

```sh
make test
```
