from src.lexer import File, Position, Token
import src.transform as t
import re

class Error:
    def __init__(self, msg: str, start: Position, stop: Position):
        self.name, self.msg, self.start, self.stop = "error", msg, start, stop
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f"{self.name}: {self.msg} (ln {self.start.ln}, col {self.start.col})\n" + \
        "\n".join(self.start.file.text.split("\n")[self.start.ln-1:self.stop.ln])
class MatchError(Error):
    def __init__(self, msg: str, pattern: str, start: Position, stop: Position):
        super().__init__(f"{msg} ('{pattern}')", start, stop)
        self.name = "mactch error"
class IDNotDefinedError(Error):
    def __init__(self, id: str, start: Position, stop: Position):
        super().__init__(f"id {id} not defined", start, stop)
        self.name = "id not defined error"
class PatternMatchError(Error):
    def __init__(self, e):
        super().__init__(f"cannot match {e}", e.start, e.stop)
        self.name = "pattern match error"

class LangError:
    def __init__(self, msg: str, start: Position, stop: Position):
        self.name, self.msg, self.start, self.stop = "error", msg, start, stop
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f"{self.start.file.fn}\n" + \
               f"{self.name}: {self.msg} (ln {self.start.ln}, col {self.start.col})\n" + \
               "\n".join(self.start.file.text.split("\n")[self.start.ln-1:self.stop.ln])
class UnexpectedError(LangError):
    def __init__(self, token: dict):
        super().__init__(f"unexpected {token['type']}", token["start"], token["stop"])
        self.name = "syntax error"

def Token(type: str, value, start: Position, stop: Position): return {"type": type, "value": value, "start": start, "stop": stop}

def lex(fn: str, text: str, lexer: t.Lexer) -> list:
    file = File(fn, text)
    pos = Position(-1, 1, -1, file)
    pos.advance()
    tokens = []
    def match(pattern: str):
        try: m = re.search(pattern, pos.sub())
        except re.error as e: return None, MatchError(e.msg, pattern, pos.copy(), pos.copy())
        if m: return m.string[m.start():m.end()] if pos.sub().startswith(m.string[m.start():m.end()]) else None, None
        return None, None
    while pos.char() is not None:
        matched = False
        for s in lexer.ignore:
            m, err = match(s.value)
            if err: return None, err
            if m:
                matched = True
                pos.advance(len(m))
                break
        if matched: continue
        for token in lexer.tokens:
            if isinstance(token, t.ValueToken):
                for s in token.strs:
                    m, err = match(s.value)
                    if err: return None, err
                    if m:
                        matched = True
                        token_, start = token, pos.copy()
                        pos.advance(len(m))
                        tokens.append(Token(token_.name, m, start, pos.copy()))
                        break
                if matched: break
                continue
            if isinstance(token, t.TokenMatch):
                for s in token.strs:
                    m, err = match(s.value)
                    if err: return None, err
                    if m:
                        matched = True
                        token_, start = token, pos.copy()
                        pos.advance(len(m))
                        tokens.append(Token(token_.name, m, start, pos.copy()))
                        break
                if matched: break
                continue
    tokens.append(Token(t.ID("eof", pos.copy(), pos.copy()), None, pos.copy(), pos.copy()))
    return tokens, None
def parse(tokens: list, parser: t.Parser, DEBUG: bool = False) -> dict:
    global indent, idx, token
    indent = 0
    idx = 0
    token = tokens[idx]
    def debug(name: str, x):
        if not DEBUG: return
        global indent, token
        print(f"{' '*indent}[{token['type']}]    {name} {x}")
    def debug_enter(name: str, x):
        if not DEBUG: return
        global indent, token
        print(f"{' '*indent}[{token['type']}] -> {name} {x}")
        indent += 1
    def debug_exit(name: str, x, *results):
        if not DEBUG: return
        global indent, token
        indent -= 1
        print(f"{' '*indent}[{token['type']}] <- {name} {x} ({', '.join([(str(result) if result is not None else '') for result in results])})")
    def update():
        global token, idx
        if idx < len(tokens): token = tokens[idx]
    def advance():
        global idx, token
        idx += 1
        update()
    def next():
        global token
        token_ = token.copy()
        advance()
        return token_
    def match_any(x):
        if isinstance(x, t.ID): return visit_layer(x)
        if isinstance(x, t.Token): return match_token(x)
        if isinstance(x, t.Group): return match_group(x)
        return None, PatternMatchError(x)
    def match_token(tok: t.Token):
        debug_enter("token", tok)
        if token["type"].value == tok.value[0]:
            debug_exit("token", tok, token["type"])
            return next(), None
        debug_exit("token", tok, False)
        return False, None
    def match_group(group: t.Group):
        debug_enter("group", group)
        for e in group.group:
            match, err = match_any(e)
            if err:
                debug_exit("group", group, match["type"] if match else match, True if err else None)
                return None, err
            if match:
                debug_exit("group", group, match["type"] if match else match)
                return match, None
        debug_exit("group", group, False)
        return False, None
    def match_layer(layer: t.Layer):
        global idx
        match = True
        debug_enter("patterns", len(layer.patterns))
        for to in layer.patterns:
            idx_ = idx
            debug("pattern", to.pattern.pattern)
            if isinstance(to, t.To):
                rec = []
                for e in to.pattern.pattern:
                    match, err = match_any(e)
                    if err:
                        debug_exit("pattern", to.pattern.pattern, None, True)
                        return None, err
                    if not match: break
                    rec.append(match)
                if match:
                    if isinstance(to.node, t.Int):
                        return rec[to.node.value-1], None
                    node = {"type": to.node.name.value}
                    node_vars = to.node.vars
                    for k in node_vars:
                        if node_vars[k].value-1 >= len(rec): raise Exception("index error for patterns")
                        node[k] = rec[+node_vars[k].value-1]
                    debug_exit("pattern", to.pattern.pattern, node["type"] if node else node)
                    return node, None
            idx = idx_
            update()
        if layer.link_layer: return visit_layer(layer.link_layer)
        return False, None
    def visit_layer(name: t.ID):
        debug_enter("layer", name)
        if name.value == "UNEXPECTED":
            debug_exit("layer", name, None, "UnexpectedError")
            return None, UnexpectedError(token)
        layer = parser.get_layer(name)
        if not layer:
            debug_exit("layer", name, None, "IDNotDefinedError")
            return None, IDNotDefinedError(name, parser.start, parser.stop)
        match, err = match_layer(layer)
        debug_exit("layer", name, match["type"] if match else match, True if err else None)
        return match, err
    ast, err = visit_layer(parser.start_layer)
    return ast, err

def from_file(fn: str, lang: t.Language, debug: bool = False) -> dict:
    try:
        with open(fn, "r") as f:
            text = f.read()
            tokens, err = lex(fn, text, lang.lexer)
            if debug:
                for tok in tokens: print(tok)
            if err: return None, err
            ast, err = parse(tokens, lang.parser, debug)
            if err: return None, err
            if debug: print(ast)
            return ast, err
    except FileNotFoundError as e:
        return None, f"file '{fn}' not found in cwd"


def from_text(text: str, lang: t.Language, debug: bool = False) -> dict:
    tokens, err = lex("<text-input>", text, lang.lexer)
    if debug:
        for tok in tokens: print(tok)
    if err: return None, err
    ast, err = parse(tokens, lang.parser, debug)
    if err: return None, err
    if debug: print(ast)
    return ast, err
