# Decisions

## ANTLR jar version 4.13.2

## ANTLR4 (Python3 target) instead of Flex/Bison

Decision: Compiler front-end built using ANTLR4 with Python3 target, not Flex/Bison as suggested in the project manual's reference stack.

Why: Confirmed with instructor and approved explicitly. ANTLR provides built-in error recovery (Bison requires manual error production rules), no separate C compilation step (faster iteration), and Python target integrates directly with the rest of the pipeline without needing GCC or a Makefile dependency chain. For a semester-long lab, this reduces friction and lets more time focus on compiler design rather than build tooling.

Alternative considered: Flex/Bison stack as documented in the manual, but this required learning additional tools (lex/yacc syntax) and added a C compilation layer that the Python codebase would need to wrap anyway.

Tradeoff / risk: ANTLR deviates from the manual's reference toolchain, requiring explicit documented justification in the report. Mitigated by getting instructor approval upfront and documenting the decision clearly here and in the project report's Architecture chapter.

---

## TAC as terminal output (no execution stage)

Decision: Compiler front-end produces Three Address Code text output and stops. No machine code generation, assembly output, or runtime execution is included.

Why: Section 4.6 of the project manual explicitly states "TAC is the final required output... You are not required to translate TAC into machine code, assembly, or any executable form." The scope of the lab is to demonstrate how compiler phases communicate, not to build a complete toolchain. A compiler that prints correct TAC for a valid program has met the requirement; anything beyond that is out of scope.

Alternative considered: Extending the pipeline to emit assembly or a simple bytecode interpreter, but this would consume time better spent on semantic analysis correctness and documentation, and Section 6 explicitly warns "Do not let scope creep distract you from delivering a complete, correct front-end."

Tradeoff / risk: Programs cannot actually _run_ — they only produce an intermediate representation. This is intentional and correct per the spec, but worth clarifying in documentation and demos so this design choice isn't mistaken for an incomplete implementation.

---

## --tokens and --symtable diagnostic CLI flags

Decision: Added `--tokens` and `--symtable` command-line flags to print the token stream and symbol table state after compilation, respectively. These are diagnostic-only and not required by the project spec.

Why: These flags make the internal compiler stages (lexer, symbol table) directly visible and inspectable during live demonstration or viva questioning, without needing to add print statements under pressure or modify the actual compiler code. A viva instructor might ask "show me what the symbol table looks like at this point" — having a `--symtable` flag available is cleaner than trying to rebuild and re-instrument the code on the spot.

Alternative considered: Leaving these as internal debugging hooks only, or documenting them as "not available for demo." But given that symbol table and token inspection are natural questions in a compiler viva, having them as official flags adds professionalism and confidence.

Tradeoff / risk: Adds two small functions to `main.py` and one read-only method to `SymbolTable`, but these have zero effect on compilation behavior and are straightforward to test. No meaningful risk; purely additive.

---

## Python module invocation via `python -m src.main`

Decision: CLI is invoked as `python -m src.main <file>`, not `python src/main.py`.

Why: The `-m` flag tells Python to import the module within its package context, which makes relative imports (`from src.ast.printer import ...`) resolve correctly. Direct filesystem invocation (`python src/main.py`) breaks package imports because Python doesn't know `src/` is a package without the module system.

Alternative considered: Direct filesystem path (`python src/main.py`), but this requires either adding `src/` to PYTHONPATH manually or structuring imports differently, which complicates usage and documentation.

Tradeoff / risk: Users must understand `python -m` invocation pattern; documented clearly in README so this isn't a surprise.
