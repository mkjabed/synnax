"""
test_semantic_analyzer.py — hand-built mock AST nodes, no real parser.

Same spirit as test_symbol_table.py: manually constructs AST node
instances in the exact shape the real parser visitor will eventually
produce (Day 5), so rules 1-3 are fully verified before that
integration happens.

Each of the first three tests corresponds directly to one of the
required tests/semantic_errors/*.mini files — same scenario, expressed
as constructed nodes here instead of Mini-language source text.
"""

from src.ast.nodes import (
    ProgramNode, VarDeclNode, AssignNode, PrintNode, BlockNode, IfNode,
    IdentifierNode, IntLiteralNode,
)
from src.semantic.semantic_analyzer import SemanticAnalyzer


def test_undeclared_variable_use_is_reported():
    # int x;
    # x = 5;
    # print y;      <- y was never declared
    program = ProgramNode(statements=[
        VarDeclNode(line=1, var_type="int", name="x"),
        AssignNode(line=2, name="x", value=IntLiteralNode(line=2, value=5)),
        PrintNode(line=3, value=IdentifierNode(line=3, name="y")),
    ])

    errors = SemanticAnalyzer().analyze(program)

    assert len(errors) == 1
    assert errors[0].rule == "undeclared_variable"
    assert errors[0].line == 3


def test_redeclaration_in_same_scope_is_reported():
    # int x;
    # int x;      <- redeclared in the same (global) scope
    program = ProgramNode(statements=[
        VarDeclNode(line=1, var_type="int", name="x"),
        VarDeclNode(line=2, var_type="int", name="x"),
    ])

    errors = SemanticAnalyzer().analyze(program)

    assert len(errors) == 1
    assert errors[0].rule == "redeclaration"
    assert errors[0].line == 2


def test_scope_violation_is_reported_and_distinguished_from_undeclared():
    # int x;
    # x = 1;
    # if (x) {
    #     int inner;
    #     inner = 42;
    #     print inner;      <- fine, still inside the block
    # }
    # print inner;          <- scope violation: inner's block has closed
    program = ProgramNode(statements=[
        VarDeclNode(line=1, var_type="int", name="x"),
        AssignNode(line=2, name="x", value=IntLiteralNode(line=2, value=1)),
        IfNode(
            line=4,
            condition=IdentifierNode(line=4, name="x"),
            then_block=BlockNode(line=4, statements=[
                VarDeclNode(line=5, var_type="int", name="inner"),
                AssignNode(line=6, name="inner", value=IntLiteralNode(line=6, value=42)),
                PrintNode(line=7, value=IdentifierNode(line=7, name="inner")),
            ]),
            else_block=None,
        ),
        PrintNode(line=9, value=IdentifierNode(line=9, name="inner")),
    ])

    errors = SemanticAnalyzer().analyze(program)

    assert len(errors) == 1
    assert errors[0].rule == "scope_violation"   # NOT "undeclared_variable"
    assert errors[0].line == 9


def test_shadowing_in_nested_scope_reports_no_error():
    # int x;
    # if (x) { int x; }      <- legal shadow, not a redeclaration
    program = ProgramNode(statements=[
        VarDeclNode(line=1, var_type="int", name="x"),
        IfNode(
            line=2,
            condition=IdentifierNode(line=2, name="x"),
            then_block=BlockNode(line=2, statements=[
                VarDeclNode(line=2, var_type="float", name="x"),
            ]),
            else_block=None,
        ),
    ])

    errors = SemanticAnalyzer().analyze(program)

    assert errors == []


def test_valid_program_reports_no_errors():
    # int x;
    # x = 5;
    # print x;
    program = ProgramNode(statements=[
        VarDeclNode(line=1, var_type="int", name="x"),
        AssignNode(line=2, name="x", value=IntLiteralNode(line=2, value=5)),
        PrintNode(line=3, value=IdentifierNode(line=3, name="x")),
    ])

    errors = SemanticAnalyzer().analyze(program)

    assert errors == []
