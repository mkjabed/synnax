# Formal Grammar Specification — Mini Language

This document defines the complete context-free grammar (CFG) for the language specified in Section 5 of the project manual, in BNF notation, as implemented via ANTLR4 (split lexer/parser grammars: `MiniLexer.g4` and `MiniParser.g4`).

## Notation Key

- `::=` means "is defined as"
- `|` means "or" (alternative productions)
- `*` means "zero or more repetitions"
- `[ ]` means "optional" (zero or one occurrence)
- `( )` groups alternatives or repeated sequences
- `" "` denotes a literal terminal (keyword, operator, or punctuation)
- `<angle-brackets>` denote non-terminals (grammar rules)
- `UPPERCASE` denotes lexical terminals defined in the Lexical Elements section

---

## 1. Program Structure

```
<program>   ::= <statement>*
```

A program is simply a sequence of zero or more statements.

---

## 2. Statements

```
<statement> ::= <var-decl>
              | <assignment>
              | <if-stmt>
              | <while-stmt>
              | <print-stmt>
              | <block>

<var-decl>   ::= <type> IDENTIFIER ";"
<type>       ::= "int" | "float" | "bool"

<assignment> ::= IDENTIFIER "=" <expr> ";"

<print-stmt> ::= "print" <expr> ";"

<block>      ::= "{" <statement>* "}"

<if-stmt>    ::= "if" "(" <expr> ")" <block> [ "else" <block> ]

<while-stmt> ::= "while" "(" <expr> ")" <block>
```

**Note:** `<block>` is recursive with `<statement>`, which is what gives nested `{ }` scoping. The symbol table's scope stack pushes a new scope on entering a `<block>` and pops it on exit.

---

## 3. Expressions and Operator Precedence

Precedence is encoded structurally by layering rules — tightest-binding at the bottom, loosest at the top. This avoids ambiguity without needing separate precedence-declaration syntax.

```
<expr>        ::= <logical-or>

<logical-or>  ::= <logical-and> ( "||" <logical-and> )*

<logical-and> ::= <logical-not> ( "&&" <logical-not> )*

<logical-not> ::= "!" <logical-not> | <relational>

<relational>  ::= <arith-expr> ( ( "<" | ">" | "<=" | ">=" | "==" | "!=" ) <arith-expr> )?

<arith-expr>  ::= <term> ( ( "+" | "-" ) <term> )*

<term>        ::= <factor> ( ( "*" | "/" | "%" ) <factor> )*

<factor>      ::= INT_LITERAL
                 | FLOAT_LITERAL
                 | BOOL_LITERAL
                 | IDENTIFIER
                 | "(" <expr> ")"
```

Precedence, loosest to tightest: `||` → `&&` → `!` → relational (`< > <= >= == !=`) → additive (`+ -`) → multiplicative (`* / %`) → atoms.

**Design decision — `!` binds tighter than relational operators.** `<logical-not>` sits directly above `<relational>` in the layering, so `!` only negates a single factor-level value (an identifier, literal, or parenthesized group) — not a full comparison. Concretely: `!a > b` parses as `(!a) > b`, **not** `!(a > b)`. Negating a comparison requires explicit parentheses: `!(a > b)`. This matches standard C-family convention and avoids the ambiguity of guessing intent — it also keeps the semantic analyzer simpler, since `!`'s operand type expectation (boolean) is locally obvious from the grammar shape alone.

**Design decision — `<relational>` allows only one comparison, not a chain.** The `( ... )?` (optional, not `*`) means `a < b < c` is not a valid expression in this language, unlike Python-style chained comparisons. This matches how `bool` is treated as a first-class but non-chainable type here, consistent with C/Java/C++.

---

## 4. Lexical Elements (Terminals)

```
IDENTIFIER    ::= ( LETTER | "_" ) ( LETTER | DIGIT | "_" )*
INT_LITERAL   ::= DIGIT+
FLOAT_LITERAL ::= DIGIT+ "." DIGIT+
BOOL_LITERAL  ::= "true" | "false"

LETTER        ::= "a".."z" | "A".."Z"
DIGIT         ::= "0".."9"
```

**Keywords** (reserved, cannot be used as identifiers): `int`, `float`, `bool`, `if`, `else`, `while`, `print`, `true`, `false`

**Operators:**

- Arithmetic: `+` `-` `*` `/` `%`
- Relational: `<` `>` `<=` `>=` `==` `!=`
- Logical: `&&` `||` `!`

**Delimiters:** `{` `}` `(` `)` `;`

**Comments** (design decision — not specified exactly by the manual, chosen to match C-family convention):

- Single-line: `// ...` to end of line
- Block: `/* ... */`

Both are discarded by the lexer, never emitted as tokens.

**Whitespace** (spaces, tabs, newlines): discarded, never emitted as tokens.

**Invalid tokens:** any character sequence matching none of the above rules is reported as a lexical error with the line number, rather than silently skipped or crashing the lexer.

---

## 5. Worked Example

Tracing the manual's own sample program (Section 5.5) against this grammar:

```
int x;
int y;
bool flag;
x = 10;
y = 0;
flag = true;
while (x > 0) {
    y = y + x;
    x = x - 1;
}
if (flag == true) {
    print y;
} else {
    print x;
}
```

- `int x;`, `int y;`, `bool flag;` → three `<var-decl>` statements.
- `x = 10;` → `<assignment>`, right-hand side `10` reduces `<expr>` → `<logical-or>` → ... → `<factor>` → `INT_LITERAL`.
- `while (x > 0) { ... }` → `<while-stmt>`, condition `x > 0` reduces through `<relational>` (one comparison, no chaining needed), body is a `<block>` containing two statements.
- `if (flag == true) { ... } else { ... }` → `<if-stmt>` with both branches present, condition `flag == true` is a single `<relational>` comparison between two `<factor>`s (an `IDENTIFIER` and a `BOOL_LITERAL`).
