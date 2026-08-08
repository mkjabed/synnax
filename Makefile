generate:
	antlr4 -Dlanguage=Python3 -visitor -no-listener src/lexer/MiniLexer.g4
	antlr4 -Dlanguage=Python3 -visitor -no-listener -lib src/lexer src/parser/MiniParser.g4

run:
	python -m src.main $(FILE)

test:
	pytest -q
