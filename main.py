import src.lexer as lexer

with open("tests/test.llp", "r") as f:
    tokens = lexer.tokenize("tests/test.llp", f.read())
    for tok in tokens: print(tok)
    print()