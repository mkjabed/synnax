"""
src/ast/nodes.py — the AST node contract, as real code.

Matches docs/ast-schema.md exactly. This file is intentionally just data
(plain dataclasses, no logic) — it's the shared shape both halves of the
project build against. Jabed's real parser visitor (Day 5) will construct
these same classes from a real parse tree; until then, this module is
also what lets the semantic analyzer be tested against hand-built mock
AST nodes.

NOTE ON THE PACKAGE NAME: this lives at src/ast/, which — if imported
carelessly as a bare top-level "ast" — would shadow Python's own
built-in `ast` module. Always import from here as `src.ast.nodes`,
never a bare `from ast.nodes import ...`.
"""

from dataclasses import dataclass


class Stmt:
    """Marker base for anything that is a statement."""
    pass


class Expr:
    """Marker base for anything that produces a value."""
    pass


# ---------------- top level ----------------

@dataclass
class ProgramNode:
    statements: list[Stmt]


# ---------------- statements ----------------

@dataclass
class VarDeclNode(Stmt):
    line: int
    var_type: str          # "int" | "float" | "bool"
    name: str


@dataclass
class AssignNode(Stmt):
    line: int
    name: str
    value: Expr


@dataclass
class PrintNode(Stmt):
    line: int
    value: Expr


@dataclass
class BlockNode(Stmt):
    line: int
    statements: list[Stmt]


@dataclass
class IfNode(Stmt):
    line: int
    condition: Expr
    then_block: BlockNode
    else_block: BlockNode | None  # None when there's no else


@dataclass
class WhileNode(Stmt):
    line: int
    condition: Expr
    body: BlockNode


# ---------------- expressions ----------------

@dataclass
class BinaryOpNode(Expr):
    line: int
    op: str                # "||" "&&" "<" ">" "<=" ">=" "==" "!="
                            # "+" "-" "*" "/" "%"
    left: Expr
    right: Expr


@dataclass
class UnaryNotNode(Expr):
    line: int
    operand: Expr


@dataclass
class IdentifierNode(Expr):
    line: int
    name: str


@dataclass
class IntLiteralNode(Expr):
    line: int
    value: int


@dataclass
class FloatLiteralNode(Expr):
    line: int
    value: float


@dataclass
class BoolLiteralNode(Expr):
    line: int
    value: bool
