from antlr4.tree.Tree import TerminalNodeImpl

from src.ast.nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    PrintNode,
    ProgramNode,
    UnaryNotNode,
    VarDeclNode,
    WhileNode,
)
from src.parser.MiniParser import MiniParser
from src.parser.MiniParserVisitor import MiniParserVisitor


class AstBuilder(MiniParserVisitor):
    def visitProgram(self, ctx: MiniParser.ProgramContext):
        return ProgramNode(statements=[self.visit(stmt) for stmt in ctx.statement()])

    def visitStatement(self, ctx: MiniParser.StatementContext):
        return self.visit(ctx.getChild(0))

    def visitVarDecl(self, ctx: MiniParser.VarDeclContext):
        name_token = ctx.IDENTIFIER().getSymbol()
        return VarDeclNode(
            line=name_token.line,
            var_type=ctx.type_().getText(),
            name=name_token.text,
        )

    def visitAssignment(self, ctx: MiniParser.AssignmentContext):
        name_token = ctx.IDENTIFIER().getSymbol()
        return AssignNode(
            line=name_token.line,
            name=name_token.text,
            value=self.visit(ctx.expr()),
        )

    def visitPrintStmt(self, ctx: MiniParser.PrintStmtContext):
        return PrintNode(
            line=ctx.PRINT().getSymbol().line,
            value=self.visit(ctx.expr()),
        )

    def visitBlock(self, ctx: MiniParser.BlockContext):
        return BlockNode(
            line=ctx.LBRACE().getSymbol().line,
            statements=[self.visit(stmt) for stmt in ctx.statement()],
        )

    def visitIfStmt(self, ctx: MiniParser.IfStmtContext):
        blocks = ctx.block()
        return IfNode(
            line=ctx.IF().getSymbol().line,
            condition=self.visit(ctx.expr()),
            then_block=self.visit(blocks[0]),
            else_block=self.visit(blocks[1]) if len(blocks) > 1 else None,
        )

    def visitWhileStmt(self, ctx: MiniParser.WhileStmtContext):
        return WhileNode(
            line=ctx.WHILE().getSymbol().line,
            condition=self.visit(ctx.expr()),
            body=self.visit(ctx.block()),
        )

    def visitExpr(self, ctx: MiniParser.ExprContext):
        return self.visit(ctx.logicalOr())

    def visitLogicalOr(self, ctx: MiniParser.LogicalOrContext):
        return self._visit_left_associative_chain(ctx)

    def visitLogicalAnd(self, ctx: MiniParser.LogicalAndContext):
        return self._visit_left_associative_chain(ctx)

    def visitLogicalNot(self, ctx: MiniParser.LogicalNotContext):
        if ctx.NOT() is None:
            return self.visit(ctx.relational())
        return UnaryNotNode(
            line=ctx.NOT().getSymbol().line,
            operand=self.visit(ctx.logicalNot()),
        )

    def visitRelational(self, ctx: MiniParser.RelationalContext):
        return self._visit_left_associative_chain(ctx)

    def visitArithExpr(self, ctx: MiniParser.ArithExprContext):
        return self._visit_left_associative_chain(ctx)

    def visitTerm(self, ctx: MiniParser.TermContext):
        return self._visit_left_associative_chain(ctx)

    def visitFactor(self, ctx: MiniParser.FactorContext):
        if ctx.INT_LITERAL() is not None:
            token = ctx.INT_LITERAL().getSymbol()
            return IntLiteralNode(line=token.line, value=int(token.text))
        if ctx.FLOAT_LITERAL() is not None:
            token = ctx.FLOAT_LITERAL().getSymbol()
            return FloatLiteralNode(line=token.line, value=float(token.text))
        if ctx.TRUE() is not None:
            return BoolLiteralNode(line=ctx.TRUE().getSymbol().line, value=True)
        if ctx.FALSE() is not None:
            return BoolLiteralNode(line=ctx.FALSE().getSymbol().line, value=False)
        if ctx.IDENTIFIER() is not None:
            token = ctx.IDENTIFIER().getSymbol()
            return IdentifierNode(line=token.line, name=token.text)
        return self.visit(ctx.expr())

    def _visit_left_associative_chain(self, ctx):
        node = self.visit(ctx.getChild(0))
        child_index = 1
        while child_index < ctx.getChildCount():
            op_node = ctx.getChild(child_index)
            right = self.visit(ctx.getChild(child_index + 1))
            node = BinaryOpNode(
                line=self._line_of(op_node),
                op=op_node.getText(),
                left=node,
                right=right,
            )
            child_index += 2
        return node

    @staticmethod
    def _line_of(node) -> int:
        if isinstance(node, TerminalNodeImpl):
            return node.getSymbol().line
        return node.start.line
