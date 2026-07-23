# Mini Language Compiler — Roadmap v3 (aligned to Metropolitan University Project Manual)

**Scope:** One fixed language per Section 5 of the manual (int/float/bool, arithmetic/relational/logical operators, if/if-else/while, print, nested-block scoping — no functions, arrays, or for-loops in core scope). Solo execution. Tooling: ANTLR4 (Python target), pending final in-class confirmation — Flex/Bison as documented fallback if she says otherwise, which the manual gives no reason to expect.

**Deadline:** 9 August (per your update — note the manual itself states 31 July with no extensions in bold; if this is a confirmed extension from your teacher, worth having that in writing too, same reasoning as the ANTLR confirmation). Today is 18 July — that gives 22 working days before submission, treated below as 3 weeks plus a short buffer.

**What changed from the earlier plan, and why:**

- **One language, not four.** Section 3 explicitly forbids substituting your own language. This removes the "shared core across languages" problem entirely — there's one frontend to build, which is _less_ total work than previously planned, not more.
- **Intermediate Code Generation (TAC) is now a real milestone, not an omission.** It's 15% of the grade — more than AST construction or the symbol table individually — and it was missing from the original plan entirely.
- **Basic error recovery is restored**, not scoped out. Section 4.2 requires it explicitly. ANTLR gives you more of this for free than Bison does (see Milestone 1.2), which is a strong, honest talking point for your viva.
- **The web app is demoted to an explicit, optional, end-of-project bonus.** Section 14 lists a GUI as bonus tooling, worth pursuing only after core requirements (Section 4) are solid — it was consuming a third of the old plan for zero required credit.
- **Documentation is structured to Section 12's exact chapter list from day one**, so `docs/decisions.md` (kept running since setup) becomes source material for the report, not a Week 3 scramble.
- **Testing is mapped to Section 15's named categories exactly**, not generic coverage: 1 valid-to-TAC program, 1 lexical error, 1 syntax error, and one test per each of the six semantic rules in Section 4.5 — 9 test programs minimum, each named for what it demonstrates.

---

## Before Day 1

- Confirm ANTLR with your teacher next class, as planned. Also worth asking, briefly: whether a Python-based toolchain is fine given Section 7 lists GCC/Makefile — you're not expecting a "no," but a paper trail on a 40%-of-grade deliverable is cheap insurance, and asking shows exactly the kind of diligence this manual is rewarding.
- Install a JVM + ANTLR, confirm `antlr4 -Dlanguage=Python3 Test.g4` runs cleanly on a trivial grammar.
- `git init` the skeleton below and commit it. You're solo, so the multi-contributor commit-tracking concern in Section 9 doesn't apply to you directly — but "regular, meaningful commits from day one, not one big commit near the deadline" is still explicitly assessed, and it's also just how real projects are built. Good instinct to keep this habit regardless of group size.
- Start `docs/decisions.md` today — one paragraph per major decision, written the day you make it. This is the single highest-leverage habit in this whole roadmap: it turns Chapter 15 (Challenges) and Chapter 17 (Conclusion) of your report from a Week-3 reconstruction into a copy-edit job.
- Write out Section 5's grammar informally in your own notes before touching ANTLR syntax — knowing the language cold before encoding it in a tool is what makes the formal CFG chapter (Section 12.7) something you can defend, not something you generated backward from working code.

---

## Repository Structure

Adapted from the manual's Section 8 suggested layout — the manual's tree has no folder for intermediate code generation despite it being a required module (Section 4.6), so `src/codegen/` is an explicit, documented addition, not a deviation.

```
project-root/
├── docs/
│   ├── report.md              # final report, chapters mirror Section 12 exactly
│   ├── decisions.md           # running log, written as you go
│   └── cfg.md                 # formal grammar specification
├── src/
│   ├── lexer/                 # MiniLexer.g4 — split lexer grammar
│   ├── parser/                # MiniParser.g4 — split parser grammar (tokenVocab=MiniLexer)
│   ├── ast/                   # AST node definitions + tree-building visitor
│   ├── symbol_table/          # scope stack, declare/lookup
│   ├── semantic/              # type checking, all 6 rules from 4.5
│   └── codegen/               # TAC generator — documented as an added-but-required folder
├── playground/
│   └── manual_lexer.py        # hand-written lexer, defense artifact
├── tests/
│   ├── valid/                 # 1+ program, clean compile through to TAC
│   ├── lexical_errors/
│   ├── syntax_errors/
│   └── semantic_errors/       # one file per rule in Section 4.5 (6 files)
├── examples/                  # representative sample programs for the report
├── Makefile                   # wraps ANTLR generation + run/test commands (see note below)
├── .gitignore                 # exclude ANTLR-generated lexer/parser code
└── README.md
```

**On the Makefile:** the manual assumes a Flex/Bison/GCC toolchain where `make` builds native binaries. With ANTLR/Python there's no compilation step in that sense — so the Makefile instead wraps `antlr4` code generation, running the compiler on a file, and running the test suite (`make generate`, `make run FILE=...`, `make test`). Document this substitution explicitly in the README and report — it satisfies the spirit of "one command to build and run," which is what's actually being assessed.

**On split vs. combined ANTLR grammars:** ANTLR allows one combined `.g4` file with both lexer and parser rules, but this project uses **split grammars** — `MiniLexer.g4` and `MiniParser.g4` (the parser referencing the lexer via `options { tokenVocab=MiniLexer; }`) — specifically to mirror the Flex (`.l`) / Bison (`.y`) separation the manual's reference toolchain uses, and to make the `src/lexer/` vs. `src/parser/` folder split real rather than arbitrary. This is a clean, honest answer if asked why two files instead of one.

---

## Week 1 (Jul 18–24) — Formal Grammar, Lexer, Parser, AST

**Goal:** source → tokens → parse tree → AST, for the full Section 5 language, with basic error recovery working.

### Milestone 1.1 — Formal CFG and Lexical Analysis (Jul 18–20, ~9–10 hrs)

**Concepts to study first:** regular languages vs. context-free grammars; DFA-based scanning; how Flex's longest-match rule and keyword/identifier ordering works (you'll explain this even though ANTLR does the equivalent for you); how to write a CFG in standard BNF/EBNF notation for the report.

**How real compilers do it:** GCC and Clang hand-write lexers because lexing is the hottest path in a compile pass; understanding why is your answer if asked "why not always use a generic tokenizer."

**What you write:**

1. `docs/cfg.md` — the full formal grammar for Section 5's language, in BNF, written _before_ you write ANTLR syntax. This is required for Chapter 7 of the report regardless of tooling, and writing it first (rather than deriving it from working `.g4` code afterward) is what makes it defensible.
2. `playground/manual_lexer.py` — small hand-written tokenizer covering just arithmetic expressions, as a from-first-principles artifact independent of ANTLR.
3. `src/lexer/MiniLexer.g4` — keywords (`int float bool if else while print true false`), identifiers, int/float/bool literals, operators, delimiters (`{ } ( ) ;`), comments, with invalid-character sequences producing a lexical error with line number (required by 4.1).

**Validation checklist:**

- [ ] Formal CFG in `cfg.md` covers every construct in Section 5 with no ambiguity you can't explain
- [ ] `manual_lexer.py` correctly hand-traces a small arithmetic string
- [ ] ANTLR lexer generates cleanly; keyword rules precede the identifier rule
- [ ] An invalid character sequence produces a clear lexical error with line number, not a silent failure or crash

**Instructor Q&A:**

- _"Why does rule order matter for keywords vs. identifiers?"_ → longest-match ties are broken by declaration order; keywords must precede the generic identifier rule or `if` lexes as an identifier.
- _"You used ANTLR — do you understand tokenization independent of the tool?"_ → walk through `manual_lexer.py`.

### Milestone 1.2 — Parser, Error Recovery, and AST (Jul 21–24, ~14–16 hrs)

**Concepts to study first:** parse tree vs. AST; ANTLR's visitor pattern; **LALR(1) (what Bison uses) vs. ANTLR's ALL(\*) adaptive LL parsing** — you don't need to implement LALR, but you need to be able to compare the two conceptually, since the manual's reference tool is Bison and you'll be asked why yours differs.

**Error recovery — required, not optional (Section 4.2):** ANTLR's `DefaultErrorStrategy` already performs single-token insertion/deletion and follow-set-based resynchronization automatically — this is arguably _more_ automatic recovery than Bison's `error` token, which requires you to manually mark recovery points in the grammar. That comparison is a strong, honest answer if your teacher asks why you didn't use Bison's approach. What you must still do: implement a custom `ErrorListener` that **collects** syntax errors (with line numbers) instead of only printing to stderr, and verify parsing continues past at least one recoverable error rather than halting immediately.

**What you write:** `src/parser/MiniParser.g4` (parser rules — statements, expressions with correct precedence for arithmetic/relational/logical operators, if/if-else, while, nested blocks, print); `src/ast/` node definitions (`IfNode`, `BinaryOpNode`, `AssignNode`, etc., as the manual names them) and the visitor that builds them; a custom `ErrorListener`.

**Deliverables:** full parser generating correctly-precedenced ASTs; a printable/indented text-based AST view (required by 4.3 — Graphviz is bonus, not required); at least one deliberately malformed program demonstrating recovery past the first syntax error.

**Validation checklist:**

- [ ] `2 + 3 * 4` parses with correct precedence; `a && b || c` and `!a` parse correctly
- [ ] Nested `{ }` blocks parse into correctly nested AST scope structure
- [ ] A program with one syntax error still reports a second, independent error rather than stopping silently
- [ ] AST prints in readable indented text form

**Instructor Q&A:**

- _"Why does your parser recover from errors differently than Bison's `error` token?"_ → ANTLR's default strategy performs automatic single-token insertion/deletion and resynchronizes via follow sets, without needing explicit `error` productions in the grammar — a design trade-off worth being able to state plainly, not defensively.
- _"Why is the AST a separate structure from the parse tree?"_ → parse tree reflects every grammar rule including punctuation; AST keeps only semantically meaningful structure for later phases.

**End of Week 1 checkpoint:** full language lexes and parses, with real error recovery, and produces a readable AST. This alone represents 35% of the technical rubric (lexer 10% + parser 15% + AST 10%), done and testable in isolation.

---

## Week 2 (Jul 25–31) — Symbol Table, Semantic Analysis, TAC Generation

### Milestone 2.1 — Symbol Table (Jul 25–26, ~6–7 hrs)

**What you write:** scope stack supporting nested blocks (4.4's explicit requirement — a variable declared inside `if`/`while` must not be visible outside it), each entry recording name, type, scope, and declaration line.

**Validation checklist:**

- [ ] A variable declared inside a `while` block is correctly invisible after the block closes
- [ ] Redeclaration in the same scope is detected; shadowing in a nested scope is allowed

### Milestone 2.2 — Semantic Analyzer, All Six Rules (Jul 27–28, ~9–10 hrs)

**Concepts to study first:** why semantic analysis is a separate AST-walking pass from parsing; how type compatibility rules are represented as checks, not grammar productions.

**What you write, entirely by hand:** an AST visitor enforcing exactly the six rules the manual names in 4.5 — treat these as a literal checklist, not "type checking" as one vague bucket:

1. Undeclared variable use
2. Redeclaration in the same scope
3. Scope violation (using a variable outside its declaring block)
4. Type mismatch (e.g. `bool b = 5 + 3.2;`)
5. Invalid assignment (e.g. assigning a bool expression to an int)
6. Invalid expressions (e.g. logical operators on numeric operands where not permitted)

**Deliverables:** semantic analyzer producing clear, line-numbered messages for each rule; six dedicated test programs, one per rule, matching Section 15's requirement exactly.

**Instructor Q&A:**

- _"Walk me through what happens when a variable is used outside its scope."_ → the symbol table's scope stack pops the inner scope when the block closes; a lookup after that point fails, and the semantic analyzer reports it against the AST node's line number.

### Milestone 2.3 — Intermediate Code Generation, TAC (Jul 29–31, ~11–13 hrs)

**This is the phase that was missing from the earlier plan — treat it with the same weight as the parser, not as an afterthought.**

**Concepts to study first:** three-address code as a linear IR where each instruction has at most one operator and two operands; temporaries and labels; the standard patterns for translating `if`, `if-else`, and `while` into labeled jumps (this is classic material — the "Dragon Book" chapter on intermediate code generation covers exactly this).

**How real compilers do it:** GCC's GIMPLE and LLVM IR are both three-address-code-style representations, precisely because a simple, linear IR decouples "what the source language looks like" from "what optimizations and later stages need to reason about." You're building a small, direct version of that same idea.

**What you write, entirely by hand — no tool generates this, for you or for anyone using Bison either:** a TAC generator (`src/codegen/`) that walks the validated AST and emits:

- Arithmetic/relational expressions → temporaries, respecting precedence (already correct in your AST, so this is mostly straightforward translation)
- Logical expressions → **decide and document eager evaluation (compute both operands, then apply the operator) rather than short-circuit evaluation**, and record that as a deliberate scope decision in `docs/decisions.md` — short-circuit logic is legitimate future work, not a gap you need to hide
- `if` / `if-else` → conditional/unconditional jumps with labels, matching the manual's illustrative pattern
- `while` → loop label, condition check, exit label
- `print` → direct TAC print instruction

**Deliverables:** TAC generator producing output matching the manual's illustrative format (Section 4.6) for the sample program in Section 5.5; at least one non-trivial valid program compiling cleanly through to TAC output (Section 15's required category).

**Validation checklist:**

- [ ] The Section 5.5 sample program produces correct, readable TAC by hand-verification
- [ ] Nested `if` inside `while` produces correctly nested labels with no collisions
- [ ] Temporary and label names are unique across the whole program (simple incrementing counters are sufficient — don't over-engineer this)

**Instructor Q&A:**

- _"Why did you choose eager evaluation for logical operators instead of short-circuit?"_ → simpler, fully correct TAC for the required feature set; short-circuit evaluation is standard further work, explicitly scoped out given the timeline.
- _"How do you guarantee your labels don't collide?"_ → a single monotonically increasing label counter shared across the whole generation pass.

**End of Week 2 checkpoint:** the entire required pipeline (4.1–4.6) is implemented and individually testable. This is 80% of the technical rubric, done with a week and a half of runway left for testing, documentation, and presentation prep.

---

## Week 3 (Aug 1–7) — Testing, Report, CLI, Presentation Prep

### Milestone 3.1 — Testing to Section 15's Exact Categories (Aug 1–2, ~7–8 hrs)

**Deliverables (minimum 9 test programs, each named for its category):**

- `tests/valid/` — ≥1 non-trivial program, clean through to TAC
- `tests/lexical_errors/` — ≥1 invalid-token program
- `tests/syntax_errors/` — ≥1 grammar-violating program
- `tests/semantic_errors/` — 6 programs, one per rule in 4.5

Each paired with expected output, per Section 15's requirement, and runnable via `make test`.

### Milestone 3.2 — CLI Polish, README, and Screenshots (Aug 3, ~5–6 hrs)

The manual requires compilation/execution instructions and screenshots of successful builds and error handling — not a web app. Build a clean CLI entry point (`python -m mini_compiler <file>` or similar, wrapped by the Makefile), and capture screenshots of: a clean compile-to-TAC run, and each of the three error categories, for direct inclusion in the report and presentation.

**README.md — Section 8 requires this to stand on its own, separate from the report.** Write it to cover, explicitly:

- One-paragraph project summary and feature list (what subset of Section 5 is implemented)
- Exact build instructions (`make generate`, or equivalent) — someone with a fresh clone should be able to follow it with no prior context
- Exact run instructions, with a real example command against a sample file
- Exact test instructions (`make test`)
- Note on the split-grammar decision and the Makefile-as-build-automation substitution (short, 2–3 sentences — the report is where these get fully explained, README just needs to not be silent about them)

**Validation checklist:**

- [ ] A person with no context could clone the repo and get a compile running from the README alone
- [ ] Screenshots captured for: clean compile-to-TAC, one lexical error, one syntax error, one semantic error

### Milestone 3.3 — Report, Structured to Section 12 (Aug 4–6, ~10–12 hrs)

Since `docs/decisions.md` has been maintained since Day 1, this is compilation and polish, not first-draft writing. Write directly to the manual's chapter list:

Introduction → Objectives → Language Specification (with the formal CFG from `cfg.md`) → Compiler Architecture → Lexer Design → Parser Design → AST → Semantic Analysis → Symbol Table → Intermediate Code → Challenges (pull straight from `decisions.md`) → Testing → Conclusion → References.

### Milestone 3.4 — Slide Deck and Presentation Prep (Aug 7, ~6–7 hrs)

**Build the slide deck first — it's a separate required deliverable (Section 11), not just a prop for rehearsal.** Keep it short and diagram-heavy, since the manual explicitly prefers live demonstration over static slides: title/overview, language summary, the Section 2 pipeline diagram redrawn as your actual architecture, one slide per phase (lexer/parser/AST/symbol table/semantic/TAC), a challenges slide, a lessons-learned slide. Reuse the diagrams and screenshots from `docs/report.md` directly rather than redesigning content twice.

Then rehearse against Section 13's checklist explicitly: phase-by-phase walkthrough, live demo on ≥1 valid and ≥1 invalid program, live demo of all three error categories, TAC output demo, challenges faced, lessons learned. Expect on-the-spot test inputs — practice compiling a program you haven't pre-tested, live, at least once before presentation day.

**Video demonstration is explicitly optional (Section 11)** — skip it unless the buffer days end up genuinely empty; it costs real time for a deliverable that isn't required.

---

## Buffer (Aug 8–9) — Bonus Features, If and Only If Core Is Solid

Do not start here unless Sections 4 and 5 are fully implemented, tested, and documented — the manual states this explicitly, twice.

**Highest-ROI bonus if you have room:** AST visualization via Graphviz. You already have a working AST and a text-based printer from Week 1; emitting a `.dot` file is a small recursive function reusing that same structure, and a rendered tree image is a strong, low-cost addition to a live demo (Section 13 rewards exactly this). This is a better time investment than reviving the web GUI, which is a much larger lift for the same bonus category.

**Submit by end of Aug 8, treat Aug 9 as true slack, not part of the plan.** Portal-close timing and last-minute technical issues (upload failures, a bad final commit) are exactly what a same-day submission has no room to absorb — and per Section 9, late commits are penalized the same as late submission regardless of intent.

---

## AI Usage — Staying Inside Section 10, Not Just the Letter of It

You raised this yourself, and it's the right thing to be deliberate about, since Section 10 is explicit: understanding is the actual thing being graded, any part of the implementation can be probed in viva regardless of who wrote it, and failing to explain your own code costs marks even if it runs correctly and even if the explanation is for AI-assisted code specifically. A few concrete checkpoints to build into the milestones above, not just a one-time read of the policy:

- **After AI helps with any component, do a deliberate "explain-back" pass before marking the milestone done.** Rewrite comments in your own words, not the AI's — if you can't independently produce an explanation of a block, you're not done with that block yet, regardless of whether the tests pass.
- **Hand-trace one real input through the code by hand** for anything non-trivial (a parser rule, a semantic check, a TAC pattern) before moving to the next milestone. If you can't trace it on paper, you don't understand it well enough for a cold viva question yet.
- **Write `docs/decisions.md` entries in your own words, in the moment**, even for AI-assisted parts — the log is only useful as viva prep if it reflects reasoning you actually hold, not reasoning you copied down.
- **Prioritize genuine understanding hardest on the parser's error recovery and the TAC generator's label/jump patterns** — these are the least mechanical, most design-heavy phases, and the most likely places a viva question digs deeper than surface-level.
- **A working test rule of thumb:** an hour after finishing a component, try to re-explain it cold, out loud, with no notes. If you can't, that's a signal to slow down and re-derive it yourself now, not a risk to carry forward and hope doesn't come up.

---

## Cross-Cutting Notes

**On engineering practice, since you asked to keep this front and center:** writing the formal grammar before the tool syntax, keeping a running decisions log instead of reconstructing it later, treating error recovery as a stated requirement rather than a corner to cut, and scaffolding the repo structure before writing implementation code — these aren't academic formalities, they're the same habits that separate maintainable production systems from ones that only work by accident. You're already doing several of these without being told to (checking the manual against the plan before continuing, asking your teacher directly instead of assuming) — that instinct is worth trusting and repeating on every future project, not just this one.

**If time gets tight in Week 2:** protect the semantic analyzer's six rules and the TAC generator over anything else — together they're 35% of the grade and were the actual gap in the original plan. Testing and documentation can compress somewhat if `decisions.md` has been kept current; the semantic analyzer and TAC generator cannot be compressed without directly costing rubric points.
