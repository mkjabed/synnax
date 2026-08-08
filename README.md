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

Generate TAC for a valid program, including `if`, `if-else`, and `while`:

```sh
python -m src.main path/to/program.mini --tac
```

Run the automated tests:

```sh
make test
```

The test suite runs all nine required programs: one valid program through
expected TAC output, one lexical error, one syntax-recovery case, and one
program for each of the six semantic res.
