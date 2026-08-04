lexer grammar MiniLexer;

// ============================================================
// Keywords
// Must precede IDENTIFIER — ANTLR resolves same-length matches
// by declaration order, so keywords have to win the tie against
// the generic identifier pattern below.
// ============================================================
INT     : 'int';
FLOAT   : 'float';
BOOL    : 'bool';
IF      : 'if';
ELSE    : 'else';
WHILE   : 'while';
PRINT   : 'print';
TRUE    : 'true';
FALSE   : 'false';

// ============================================================
// Operators
// Multi-character operators precede their single-character
// prefixes (LE before LT, etc.) for the same tie-breaking reason.
// ============================================================
LE      : '<=';
GE      : '>=';
EQ      : '==';
NEQ     : '!=';
LT      : '<';
GT      : '>';

AND     : '&&';
OR      : '||';
NOT     : '!';

PLUS    : '+';
MINUS   : '-';
TIMES   : '*';
DIVIDE  : '/';
MOD     : '%';

ASSIGN  : '=';

// ============================================================
// Delimiters
// ============================================================
LBRACE  : '{';
RBRACE  : '}';
LPAREN  : '(';
RPAREN  : ')';
SEMI    : ';';

// ============================================================
// Literals
// FLOAT_LITERAL naturally wins over INT_LITERAL on inputs like
// "3.14" because ANTLR's lexer always matches the longest
// possible string first (maximal munch) — declaration order only
// breaks ties between equal-length matches, so this ordering is
// for grouping/readability, not strictly required for correctness.
// TRUE / FALSE (declared above, as keywords) double directly as
// the boolean literal tokens — no separate BOOL_LITERAL rule.
// ============================================================
FLOAT_LITERAL : DIGIT+ '.' DIGIT+;
INT_LITERAL   : DIGIT+;

// ============================================================
// Identifiers
// ============================================================
IDENTIFIER : (LETTER | '_') (LETTER | DIGIT | '_')*;

// ============================================================
// Comments — discarded, never emitted as tokens
// ============================================================
LINE_COMMENT  : '//' ~[\r\n]*        -> skip;
BLOCK_COMMENT : '/*' .*? '*/'        -> skip;

// ============================================================
// Whitespace — discarded, never emitted as tokens
// ============================================================
WS : [ \t\r\n]+ -> skip;

// ============================================================
// Fragments (not tokens themselves — building blocks for the
// rules above)
// ============================================================
fragment LETTER : [a-zA-Z];
fragment DIGIT  : [0-9];

// Any character that matches none of the rules above falls
// through to ANTLR's default lexer error handling, which reports
// a token recognition error with line/column — satisfying the
// manual's "invalid tokens must be reported with a line number"
// requirement without a dedicated catch-all rule.
