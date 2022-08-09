import re
from enum import Enum, auto

class File:
    def __init__(self, fn: str, text: str):
        self.fn = fn
        self.text = text
    def copy(self):
        return File(self.fn, self.text)
class Position:
    def __init__(self, idx: int, ln: int, col: int, file: File):
        self._idx = idx
        self.ln = ln
        self.col = col
        self.file = file
    def copy(self):
        return Position(self._idx, self.ln, self.col, self.file)
    @property
    def idx(self) -> int:
        return self._idx
    @idx.setter
    def idx(self, v: int):
        if 0 <= v <= len(self.file.text):
            self._idx = v
    def advance(self, steps: int = 1):
        self.idx += steps
        self.col += steps
        if self.idx < len(self.file.text):
            if self.file.text[self.idx] == "\n":
                self.col = 0
                self.ln += 1
    def next(self) -> str:
        char = self.char()
        self.advance()
        return char
    def char(self) -> str:
        return self.file.text[self.idx] if self.idx < len(self.file.text) else None
    def sub(self) -> str:
        return self.file.text[self.idx:] if self.idx < len(self.file.text) else ""
class Token:
    def __init__(self, t: str, value, start: Position, stop: Position):
        self.type = t
        self.value = value
        self.start = start
        self.stop = stop
        self.file = start.file
    def copy(self):
        return Token(self.type, self.value, self.start, self.stop)
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f"[{self.type}" + (":" + repr(self.value) if self.value is not None else "") + "]"
    def sub(self):
        return self.file.text[self.start.idx:self.stop.idx+1]

keywords = ["NAME", "EXTENTION", "LEXER", "PARSER", "TRUE", "IGNORE", "VALUE", "DELIM", "LAYER", "EXPECT", "BINARY"]
class T(Enum):
    EOF = auto()
    NL = auto()
    INT = auto()
    FLOAT = auto()
    STR = auto()
    ID = auto()
    TOKEN = auto()
    BODY_IN = auto()
    BODY_OUT = auto()
    GROUP_IN = auto()
    GROUP_OUT = auto()
    TO = auto()
    EQ = auto()
    NAME = auto()
    EXTENTION = auto()
    LEXER = auto()
    PARSER = auto()
    TRUE = auto()
    IGNORE = auto()
    VALUE = auto()
    DELIM = auto()
    LAYER = auto()
    EXPECT = auto()
    BINARY = auto()

class Lexer:
    def __init__(self, fn, text):
        self.pos, self.tokens = Position(-1, 1, -1, File(fn, text)), []
        self.pos.advance()
    def match(self, pattern: str):
        match = re.search(pattern, self.pos.sub())
        if match:
            return match.string[match.start():match.end()] \
                if self.pos.sub().startswith(match.string[match.start():match.end()]) else None
    def name(self):
        match = self.match(r"\b[a-zA-Z_]([a-zA-Z_0-9])+\b")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            if match in keywords:
                self.tokens.append(Token(T.__dict__[match], None, start, self.pos.copy()))
                return True
            self.tokens.append(Token(T.ID, match, start, self.pos.copy()))
            return True
        return False
    def int(self):
        match = self.match(r"\d+")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            self.tokens.append(Token(T.INT, int(match), start, self.pos.copy()))
            return True
        return False
    def float(self):
        match = self.match(r"\d+\.\d+")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            self.tokens.append(Token(T.FLOAT, float(match), start, self.pos.copy()))
            return True
        match = self.match(r"\.\d+")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            self.tokens.append(Token(T.FLOAT, float(match), start, self.pos.copy()))
            return True
        match = self.match(r"\d+\.")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            self.tokens.append(Token(T.FLOAT, float(match), start, self.pos.copy()))
            return True
        return False
    def str(self):
        match = self.match(r'"[^"]*"')
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            match = match[1:-1]
            match = match.replace("\\t", "\t").replace("\\n", "\n")
            self.tokens.append(Token(T.STR, match, start, self.pos.copy()))
            return True
        match = self.match(r"'[^']*'")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            match = match[1:-1]
            match = match.replace("\\t", "\t").replace("\\n", "\n")
            self.tokens.append(Token(T.STR, match, start, self.pos.copy()))
            return True
        return False
    def token(self):
        match = self.match(r'\[\w+:\w+\]')
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            match = match[1:-1].split(":")
            type_, value = match[0], match[1]
            self.tokens.append(Token(T.TOKEN, (type_, value), start, self.pos.copy()))
            return True
        match = self.match(r'\[\w+\]')
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            match = match[1:-1]
            self.tokens.append(Token(T.TOKEN, (match,), start, self.pos.copy()))
            return True
        return False
    def to(self):
        match = self.match(r"->")
        if match:
            start = self.pos.copy()
            self.pos.advance(len(match))
            self.tokens.append(Token(T.TO, None, start, self.pos.copy()))
            return True
        return False
    def lex(self):
        while self.pos.char() is not None:
            if self.pos.char() in [" ", "\t"]:
                self.pos.advance()
                continue
            if self.pos.char() == "\n":
                self.tokens.append(Token(T.NL, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.pos.char() == "{":
                self.tokens.append(Token(T.BODY_IN, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.pos.char() == "}":
                self.tokens.append(Token(T.BODY_OUT, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.pos.char() == "(":
                self.tokens.append(Token(T.GROUP_IN, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.pos.char() == ")":
                self.tokens.append(Token(T.GROUP_OUT, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.pos.char() == "=":
                self.tokens.append(Token(T.EQ, None, self.pos.copy(), self.pos.copy()))
                self.pos.advance()
                continue
            if self.to(): continue
            if self.token(): continue
            if self.name(): continue
            if self.float(): continue
            if self.int(): continue
            if self.str(): continue
            self.pos.advance()
        self.tokens.append(Token(T.EOF, None, self.pos.copy(), self.pos.copy()))
        return self.tokens, None

def tokenize(fn, text):
    lexer = Lexer(fn, text)
    return lexer.lex()