import src.lexer as lexer
import src.parser as parser

with open("tests/test.llp", "r") as f:
    tokens, err = lexer.tokenize("tests/test.llp", f.read())
    if err: exit(str(err))
    # for tok in tokens: print(tok)
    body, err = parser.parse(tokens)
    if err: exit(str(err))
    print(body)
    print()