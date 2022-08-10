from src import lexer, parser, create

with open("tests/test.llp", "r") as f:
    tokens, err = lexer.tokenize("tests/test.llp", f.read())
    if err: exit(str(err))
    # for tok in tokens: print(tok)
    body, err = parser.parse(tokens)
    if err: exit(str(err))
    # print(body)
    language, err = create.create(body)
    if err: exit(str(err))
    print(language.convTree("", ". "))