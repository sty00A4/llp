from src.lexer import File, Position, Token
import src.transform as t
import re

class Error:
    def __init__(self, msg: str, pos: Position):
        self.name, self.msg, self.pos = "error", msg, pos
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f"{self.name}: {self.msg} (ln {self.pos.ln}, col {self.pos.col})"
class MatchError(Error):
    def __init__(self, msg: str, pattern: str, pos: Position):
        super().__init__(f"{msg} ('{pattern}')", pos)
        self.name = "mactch error"

def Token(type: str, value, pos: Position): return {"type": type, "value": value, "pos": pos}

def lex(fn: str, text: str, lexer: t.Lexer) -> list:
    file = File(fn, text)
    pos = Position(-1, 1, -1, file)
    pos.advance()
    tokens = []
    def match(pattern: str):
        try: m = re.search(pattern, pos.sub())
        except re.error as e: return None, MatchError(e.msg, pattern, pos.copy())
        if m: return m.string[m.start():m.end()] if pos.sub().startswith(m.string[m.start():m.end()]) else None
    while pos.char() is not None:
        matched = False
        for s in lexer.ignore:
            m = match(s)
            if m:
                matched = True
                pos.advance(len(m))
                break
        if matched: continue
        for token in lexer.tokens:
            if isinstance(token, t.ValueToken):
                for s in token.strs:
                    m = match(s)
                    if m:
                        matched = True
                        tokens.append(Token(token.name, m, pos.copy()))
                        pos.advance(len(m))
                        break
                if matched: break
                continue
            if isinstance(token, t.Token):
                for s in token.strs:
                    m = match(s)
                    if m:
                        matched = True
                        tokens.append(Token(token.name, None, pos.copy()))
                        pos.advance(len(m))
                        break
                if matched: break
                continue
        pos.advance()
    tokens.append(Token("eof", None, pos.copy()))
    return tokens, None
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


def from_file(fn: str, lang: t.Language, debug: bool = False):
    try:
        with open(fn, "r") as f:
            text = f.read()
            tokens, err = lex(fn, text, lang.lexer)
            if debug:
                for tok in tokens: print(tok)
            if err: return None, err
            ast, err = parse(tokens, lang.parser)
            if debug: print(ast)
            return ast, err
    except FileNotFoundError as e:
        return None, f"file '{fn}' not found in cwd"


def from_text(text: str, lang: t.Language, debug: bool = False):
    tokens, err = lex("<text-input>", text, lang.lexer)
    if debug:
        for tok in tokens: print(tok)
    if err: return None, err
    ast, err = parse(tokens, lang.parser)
    if debug: print(ast)
    return ast, err
