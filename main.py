from src import lexer, parser, transform, llp

with open("tests/test.llp", "r") as f:
    tokens, err = lexer.tokenize("tests/test.llp", f.read())
    if err: exit(str(err))
    # for tok in tokens: print(tok)
    body, err = parser.parse(tokens)
    if err: exit(str(err))
    # print(body)
    lang, err = transform.transform(body)
    if err: exit(str(err))
    # print(language.convTree("", ". "))
    ast, err = llp.from_file("tests/test.math", lang, True)
    if err: exit(str(err))
