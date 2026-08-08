"""
symbol_table.py — scope stack for the Mini language.

Supports nested block scoping: a variable declared inside a block is
only visible within that block and any blocks nested inside it, never
outside it. Shadowing (redeclaring the same name in a nested scope) is
legal; redeclaring the same name in the SAME scope is not.

This module has no dependency on the AST yet — it's built and tested
against hand-built mock declare/enter/exit sequences, so it's ready to
be driven by the real AST visitor as soon as it exists.
"""

from dataclasses import dataclass


@dataclass
class SymbolEntry:
    name: str
    var_type: str      # "int" | "float" | "bool"
    scope_level: int    # 0 = global, 1 = first nested block, etc.
    declared_line: int


@dataclass(frozen=True)
class ScopeSnapshot:
    """Read-only record of a scope after it has left the active stack."""
    depth: int
    entries: tuple[SymbolEntry, ...]


class RedeclarationError(Exception):
    """Raised when a name is declared twice in the SAME scope."""
    def __init__(self, name: str, line: int, original_line: int):
        self.name = name
        self.line = line
        self.original_line = original_line
        super().__init__(
            f"'{name}' redeclared at line {line} "
            f"(originally declared at line {original_line})"
        )


class SymbolTable:
    def __init__(self):
        # Index 0 is always the global scope. It is never popped.
        self._scopes: list[dict[str, SymbolEntry]] = [{}]
        # Diagnostic history only. Lookup continues to consult _scopes alone.
        self._scope_history: list[ScopeSnapshot] = []

    @property
    def current_depth(self) -> int:
        """0 = global scope, 1 = one level of nesting, etc."""
        return len(self._scopes) - 1

    def enter_scope(self) -> None:
        """Call when entering a new block ('{')."""
        self._scopes.append({})

    def exit_scope(self) -> None:
        """Call when leaving a block ('}'). Everything declared inside
        becomes invisible again — this IS the scope-violation guarantee."""
        if len(self._scopes) == 1:
            raise RuntimeError("Cannot exit the global scope")
        self._scope_history.append(ScopeSnapshot(
            depth=self.current_depth,
            entries=tuple(self._scopes[-1].values()),
        ))
        self._scopes.pop()

    @property
    def scope_history(self) -> tuple[ScopeSnapshot, ...]:
        """Completed scopes, in exit order, for read-only diagnostics."""
        return tuple(self._scope_history)

    @property
    def active_scopes(self) -> tuple[tuple[SymbolEntry, ...], ...]:
        """Entries currently available to lookup, grouped by scope depth."""
        return tuple(tuple(scope.values()) for scope in self._scopes)

    def declare(self, name: str, var_type: str, line: int) -> None:
        """Declare a new symbol in the CURRENT (innermost) scope.

        Raises RedeclarationError if the name already exists in this
        exact scope. Declaring a name that exists in an OUTER scope is
        legal (shadowing), not a redeclaration.
        """
        current = self._scopes[-1]
        if name in current:
            raise RedeclarationError(
                name, line, current[name].declared_line
            )
        current[name] = SymbolEntry(
            name=name,
            var_type=var_type,
            scope_level=self.current_depth,
            declared_line=line,
        )

    def lookup(self, name: str) -> SymbolEntry | None:
        """Search from innermost to outermost scope. Returns None if not
        found anywhere — the caller (semantic analyzer) is responsible
        for turning that into an 'undeclared variable' or 'scope
        violation' diagnostic, since only it has the line number of the
        USE, which is what the error should report against.
        """
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None
