parser grammar MiniParser;

options {
    tokenVocab = MiniLexer;
}

program
    : statement* EOF
    ;

statement
    : varDecl
    | assignment
    | ifStmt
    | whileStmt
    | printStmt
    | block
    ;

varDecl
    : type IDENTIFIER SEMI
    ;

type
    : INT
    | FLOAT
    | BOOL
    ;

assignment
    : IDENTIFIER ASSIGN expr SEMI
    ;

printStmt
    : PRINT expr SEMI
    ;

block
    : LBRACE statement* RBRACE
    ;

ifStmt
    : IF LPAREN expr RPAREN block (ELSE block)?
    ;

whileStmt
    : WHILE LPAREN expr RPAREN block
    ;

expr
    : logicalOr
    ;

logicalOr
    : logicalAnd (OR logicalAnd)*
    ;

logicalAnd
    : logicalNot (AND logicalNot)*
    ;

logicalNot
    : NOT logicalNot
    | relational
    ;

relational
    : arithExpr ((LT | GT | LE | GE | EQ | NEQ) arithExpr)?
    ;

arithExpr
    : term ((PLUS | MINUS) term)*
    ;

term
    : factor ((TIMES | DIVIDE | MOD) factor)*
    ;

factor
    : INT_LITERAL
    | FLOAT_LITERAL
    | TRUE
    | FALSE
    | IDENTIFIER
    | LPAREN expr RPAREN
    ;
