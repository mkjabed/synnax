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

Run the automated tests:

```sh
make test
```
