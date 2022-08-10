import src.transform as t

def lex(fn: str, text: str, lexer: t.Lexer) -> list:
    # TODO: lex
    return [], None
def parse(tokens: list, parser: t.Parser):
    # TODO: parse
    return {
        "type": "BinOp",
        "left": {
            "type": "Int",
            "value": 1
        },
        "op": {
            "type": "add"
        },
        "right": {
            "type": "Int",
            "value": 1
        },
    }, None
def fromFile(fn: str, lang: t.Language):
    try:
        with open(fn, "r") as f:
            text = f.read()
            tokens, err = lex(fn, text, lang.lexer)
            if err: return None, err
            ast, err = parse(tokens, lang.parser)
            return ast, err
    except FileNotFoundError as e:
        return None, f"file '{fn}' not found in cwd"
def fromText(text: str, lang: t.Language):
    tokens, err = lex("<text-input>", text, lang.lexer)
    if err: return None, err
    ast, err = parse(tokens, lang.parser)
    return ast, err