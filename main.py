import src.lexer as lexer

with open("tests/test.lm", "r") as f:
    tokens = lexer.tokenize("tests/test.lm", f.read())
    for tok in tokens: print(tok, end=" ")
    print()