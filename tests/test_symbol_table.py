"""
test_symbol_table.py — hand-built mock scope sequences.

These don't touch the AST or parser at all — every test manually drives
enter_scope/declare/lookup/exit_scope in the exact order a real AST
visitor will eventually call them, so this module is fully verified
before the real integration happens.
"""

import pytest
from symbol_table import SymbolTable, RedeclarationError


def test_declare_and_lookup_in_global_scope():
    st = SymbolTable()
    st.declare("x", "int", line=1)

    entry = st.lookup("x")
    assert entry is not None
    assert entry.name == "x"
    assert entry.var_type == "int"
    assert entry.scope_level == 0
    assert entry.declared_line == 1


def test_lookup_of_never_declared_name_returns_none():
    st = SymbolTable()
    assert st.lookup("ghost") is None


def test_redeclaration_in_same_scope_raises():
    st = SymbolTable()
    st.declare("x", "int", line=1)

    with pytest.raises(RedeclarationError) as exc_info:
        st.declare("x", "float", line=2)

    assert exc_info.value.name == "x"
    assert exc_info.value.line == 2
    assert exc_info.value.original_line == 1


def test_shadowing_in_nested_scope_is_legal():
    # int x;          <- global, line 1
    # { int x; }       <- nested block, line 2, legal shadow
    st = SymbolTable()
    st.declare("x", "int", line=1)

    st.enter_scope()
    st.declare("x", "float", line=2)   # must NOT raise

    inner = st.lookup("x")
    assert inner.var_type == "float"
    assert inner.scope_level == 1

    st.exit_scope()

    outer = st.lookup("x")
    assert outer.var_type == "int"
    assert outer.scope_level == 0


def test_scope_violation_variable_invisible_after_block_exits():
    # if (...) { int inner; }
    # print inner;   <- should fail: inner no longer in any active scope
    st = SymbolTable()

    st.enter_scope()
    st.declare("inner", "int", line=5)
    assert st.lookup("inner") is not None   # visible while inside the block

    st.exit_scope()
    assert st.lookup("inner") is None       # invisible after the block closes


def test_nested_blocks_do_not_leak_into_each_other():
    # { int a; }
    # { print a; }   <- two SEPARATE sibling blocks, 'a' from the first
    #                   must not be visible in the second
    st = SymbolTable()

    st.enter_scope()
    st.declare("a", "int", line=1)
    st.exit_scope()

    st.enter_scope()
    assert st.lookup("a") is None
    st.exit_scope()


def test_current_depth_tracks_nesting_level():
    st = SymbolTable()
    assert st.current_depth == 0

    st.enter_scope()
    assert st.current_depth == 1

    st.enter_scope()
    assert st.current_depth == 2

    st.exit_scope()
    assert st.current_depth == 1

    st.exit_scope()
    assert st.current_depth == 0


def test_cannot_exit_global_scope():
    st = SymbolTable()
    with pytest.raises(RuntimeError):
        st.exit_scope()


def test_outer_variable_visible_from_nested_scope():
    # int x;
    # while (...) { print x; }   <- x declared outside must be visible inside
    st = SymbolTable()
    st.declare("x", "int", line=1)

    st.enter_scope()
    entry = st.lookup("x")
    assert entry is not None
    assert entry.scope_level == 0   # still reports its ORIGINAL scope level
    st.exit_scope()
