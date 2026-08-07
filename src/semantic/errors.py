"""
src/semantic/errors.py — unified semantic error format.

One shape for all six required rules (Section 4.5), so the analyzer,
the CLI, and the test suite all agree on what a semantic error looks
like, regardless of which rule produced it.
"""

from dataclasses import dataclass


@dataclass
class SemanticError:
    line: int
    rule: str       # "undeclared_variable" | "redeclaration" |
                    # "scope_violation" | "type_mismatch" |
                    # "invalid_assignment" | "invalid_expression"
    message: str
