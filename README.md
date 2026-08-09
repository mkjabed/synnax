# Synnax Mini-Language Compiler

Synnax is a Mini-language compiler front end and Three Address Code (TAC) generator. Its implementation includes lexical analysis, parsing with error recovery, AST construction, nested-scope symbol-table handling, semantic analysis, and TAC generation.

## Team

- **Mustofa Kamal Jabed**
- **Mahdi Hasan Talukder**
- **Supervised by: Mahbuba Akther Liza**

## Requirements

- Python **3.14.6**
- Java **26.0.2**
- ANTLR jar **4.13.2**, pinned in `docs/decisions.md`
- `antlr4-python3-runtime` **4.13.2**
- pytest **9.1.1**
- GNU Make **4.4.1**

The pinned ANTLR jar and installed Python runtime versions match exactly: **4.13.2**. The `make generate` target also requires the `antlr4` command-line tool.

## Build

Regenerate the lexer and parser from the split grammar files:

```sh
make generate
```

This invokes:

```sh
antlr4 -Dlanguage=Python3 -visitor -no-listener src/lexer/MiniLexer.g4
antlr4 -Dlanguage=Python3 -visitor -no-listener -lib src/lexer src/parser/MiniParser.g4
```

## Run

Run the compiler as a Python module:

```sh
python -m src.main path/to/program.mini
```

The Makefile provides an equivalent command:

```sh
make run FILE=tests/valid/valid_program.mini
```

The positional `file` argument is required. The CLI supports these flags:

- `--tokens` prints lexer tokens before parsing.
- `--symtable` prints active and closed symbol-table scopes after semantic analysis, including when semantic errors were found.
- `--tac` prints TAC only after semantic analysis succeeds.
- `--ast` prints the AST only after semantic analysis succeeds.

For successful compilation, the program prints `Compilation succeeded.` and exits with status `0`. Syntax and semantic errors print diagnostics and return status `1`. An unreadable input file is handled by `argparse` through `parser.error()` and exits with status `2`.

For example:

```sh
python -m src.main tests/valid/valid_program.mini --tac
```

## Test

Run the suite with:

```sh
make test
```

This runs `pytest -q`.

## Design Notes

The grammar is deliberately split between `src/lexer/MiniLexer.g4` and `src/parser/MiniParser.g4`. The parser grammar uses the lexer token vocabulary, mirroring the separate Flex and Bison source files of the project manual's reference toolchain.

The Makefile substitutes Python-oriented generation, execution, and test targets for a native Flex/Bison/GCC build: `generate` runs ANTLR, `run` invokes the module, and `test` runs pytest.

The project uses ANTLR4 with the Python 3 target rather than Flex/Bison. The documented rationale includes direct Python integration and ANTLR's built-in error recovery; the decisions log contrasts this with Bison, where error productions must be written manually.

TAC is the terminal output of this compiler front end: the project does not generate machine code, assembly, or an executable runtime.

`--tokens` and `--symtable` are documented diagnostic flags for inspecting lexer output and symbol-table state. The documented CLI invocation is `python -m src.main`, which preserves package-relative imports.

## Development Notes

This project was developed with assistance from AI tools (Claude, Codex) for code generation, architecture guidance, and debugging. All code was reviewed,
tested, and verified by hand to ensure correctness and understanding per the course AI usage policy (Section 10).

## Project Structure

```text
.
├── .agents/                         Agent-related repository configuration
├── .vscode/                         Visual Studio Code workspace configuration
├── docs/
│   ├── ast-schema.md                 AST node-shape contract
│   ├── cfg.md                        Formal Mini-language grammar
│   ├── decisions.md                  Running design-decision log and ANTLR pin
│   └── report.md                     Project report draft
├── examples/                         Representative Mini source programs
├── playground/
│   ├── check_lexer.py                Lexer inspection helper
│   └── manual_lexer.py               Hand-written lexer experiment
├── src/
│   ├── ast/                          AST nodes, parse-tree builder, and formatter
│   ├── codegen/                      TAC generator
│   ├── lexer/                        ANTLR lexer grammar and generated lexer artifacts
│   ├── parser/                       ANTLR parser grammar, generated parser artifacts, parser entry point, and syntax-error support
│   ├── semantic/                     Semantic analyzer and semantic-error definitions
│   ├── symbol_table/                 Nested-scope symbol-table implementation
│   ├── __init__.py                   Python package marker
│   └── main.py                       CLI entry point
├── tests/
│   ├── lexical_errors/               Invalid-character Mini input
│   ├── semantic_errors/              Inputs for assignment, expression, redeclaration, scope, type, and undeclared-variable errors
│   ├── syntax_errors/                Input with missing syntax tokens
│   ├── valid/                        Valid Mini program input
│   ├── test_ast_builder.py           AST builder tests
│   ├── test_cli_diagnostics.py       CLI diagnostic tests
│   ├── test_compiler_pipeline.py     Compiler-pipeline tests
│   ├── test_parser_semantic_integration.py  Parser/semantic integration tests
│   ├── test_semantic_analyzer.py     Semantic-analyzer tests
│   ├── test_symbol_table.py          Symbol-table tests
│   ├── test_tac_generator.py         TAC-generator tests
│   └── test_type_semantics.py        Type-semantics tests
├── conftest.py                       pytest import-path setup
├── LICENSE                           License text
├── Makefile                          ANTLR generation, run, and test targets
├── roadmap.md                        Project roadmap
├── workflow.md                       Two-person Git workflow guide
├── pytest.ini                        pytest configuration
└── README.md                         Project overview and usage
```

The listing excludes `.git`, `__pycache__`, `.antlr`, pytest-cache directories, and `.gitkeep` files.

## Documentation

- [Project report](docs/report.md)
- [Formal grammar](docs/cfg.md)
- [AST schema](docs/ast-schema.md)
- [Design decisions](docs/decisions.md)

## References

- Compiler Construction Lab: Project Manual, Metropolitan University, Bangladesh, Department of Computer Science and Engineering
- Anthropic Claude and OpenAI Codex for code assistance and architecture review
- ANTLR4 documentation (https://www.antlr.org/)
- Smith, James. _From Source Code To Machine Code: Build Your Own Compiler From Scratch_. Build Your Own X From Scratch series, 2023.
