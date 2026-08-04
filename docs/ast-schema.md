# AST Schema Contract — Mini Language

---

## Base Categories

Two abstract marker categories every concrete node falls under — not implemented directly, just for typing/organization:

```python
class Stmt:
    """Marker base for anything that is a statement."""
    pass

class Expr:
    """Marker base for anything that produces a value."""
    pass
```

---

## Program (top level)

```python
@dataclass
class ProgramNode:
    statements: list[Stmt]
```

---

## Statement Nodes

```python
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
    else_block: BlockNode | None   # None when there's no else

@dataclass
class WhileNode(Stmt):
    line: int
    condition: Expr
    body: BlockNode
```

**Note:** `BlockNode` is reused as-is for the body of `if`, `else`, and `while` — it's the same node type everywhere a `{ }` appears in the grammar, which is what makes nested scoping consistent: the symbol table pushes/pops a scope on every `BlockNode` entry/exit, regardless of what statement contains it.

---

## Expression Nodes

```python
@dataclass
class BinaryOpNode(Expr):
    line: int
    op: str            # "||" | "&&" | "<" | ">" | "<=" | ">=" | "==" | "!="
                        # | "+" | "-" | "*" | "/" | "%"
    left: Expr
    right: Expr

@dataclass
class UnaryNotNode(Expr):
    line: int
    operand: Expr      # per the CFG's tight-binding decision, this is always
                        # a <factor>-level expression, never a full <relational>

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
```

**Design decision — one `BinaryOpNode` shape for all binary operators, distinguished by the `op` string field**, rather than a separate node class per operator (`AndNode`, `OrNode`, `LessThanNode`, etc.). This keeps the node count small and means the semantic analyzer and TAC generator each only need one visitor method per *category* of binary operator (logical / relational / arithmetic), branching on `op` inside it — rather than one method per individual operator.

---

## What This Contract Guarantees, and What It Doesn't

**Guarantees:** every node has a `line` field; every statement-shaped thing is one of the seven `Stmt` subclasses above; every value-producing thing is one of the six `Expr` subclasses above; block structure (for scoping) is always a `BlockNode`.

**Does not yet guarantee:** type correctness (that's the semantic analyzer's job, operating on this same tree, not the tree's job to enforce structurally) — e.g. nothing here stops `BinaryOpNode(op="&&", left=IntLiteralNode(...), right=...)` from being constructed; catching that a `&&` operand isn't boolean happens in semantic analysis (Section 4.5's "invalid expressions" rule), not here.
