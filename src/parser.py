from src.lexer import Token, T, Position
from enum import Enum, auto

class UnexpectedError:
    def __init__(self, token: Token):
        self.token = token
    def __str__(self):
        return f"syntax error: unexpected '{self.token.sub()}' (ln {self.token.start.ln}:{self.token.stop.ln})"
class ExpectedError:
    def __init__(self, expected_type: T, token: Token):
        self.token, self.expected_type = token, expected_type
    def __str__(self):
        return f"syntax error: expected {str(self.expected_type)[2:]}, got '{self.token.sub()}' (ln {self.token.start.ln}:{self.token.stop.ln})"

class Node:
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
    def __str__(self):
        return repr(self)
class NameNode(Node):
    def __init__(self, token, start, stop):
        super().__init__(start, stop)
        self.token = token
    def __repr__(self):
        return f"(NAME {self.token})"
class ExtentionNode(Node):
    def __init__(self, token, start, stop):
        super().__init__(start, stop)
        self.token = token
    def __repr__(self):
        return f"(EXTENTION {self.token})"
class BodyNode(Node):
    def __init__(self, nodes: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.nodes = nodes
    def __repr__(self):
        return "({\n" + "\n".join([str(n) for n in self.nodes]) + "\n})"
class LexerNode(Node):
    def __init__(self, body: BodyNode, start: Position, stop: Position):
        super().__init__(start, stop)
        self.body = body
    def __repr__(self):
        return f"(LEXER {self.body})"
class ParserNode(Node):
    def __init__(self, body: BodyNode, start_layer: Token, start: Position, stop: Position):
        super().__init__(start, stop)
        self.body = body
        self.start_layer = start_layer
    def __repr__(self):
        return f"(PARSER {self.body})"
class ValueTokenNode(Node):
    def __init__(self, name: Token, strs: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.name, self.strs = name, strs
    def __repr__(self):
        return f"(VALUE {self.name} " + " ".join([str(n) for n in self.strs]) + ")"
class TokenNode(Node):
    def __init__(self, name: Token, strs: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.name, self.strs = name, strs
    def __repr__(self):
        return f"({self.name} " + " ".join([str(n) for n in self.strs]) + ")"
class IgnoreNode(Node):
    def __init__(self, strs: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.strs = strs
    def __repr__(self):
        return f"(IGNORE " + " ".join([str(n) for n in self.strs]) + ")"

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.token: Token = tokens[0]
        self.idx = 0
    def advance(self):
        self.idx += 1
        if self.idx >= len(self.tokens): self.idx = len(self.tokens) - 1
        self.token: Token = self.tokens[self.idx]
    def next(self) -> Token:
        token: Token = self.token.copy()
        self.advance()
        return token
    def lexer_stat(self):
        start = self.token.start.copy()
        if self.token.type == T.VALUE:
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            name = self.next().copy()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next().copy()
                strs.append(string)
            return ValueTokenNode(name, strs, start, stop), None
        if self.token.type == T.IGNORE:
            self.advance()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next().copy()
                strs.append(string)
            return IgnoreNode(strs, start, stop), None
        if self.token.type == T.ID:
            name = self.next().copy()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next().copy()
                strs.append(string)
            return TokenNode(name, strs, start, stop), None
        return None, UnexpectedError(self.token)
    def stat(self):
        if self.token.type == T.NAME:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            return NameNode(self.next(), start, self.token.stop.copy()), None
        if self.token.type == T.EXTENTION:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            return ExtentionNode(self.next(), start, self.token.stop.copy()), None
        if self.token.type == T.LEXER:
            start = self.token.start.copy()
            self.advance()
            body, err = self.body(self.lexer_stat)
            if err: return None, err
            return LexerNode(body, start, self.token.stop.copy()), None
        return None, UnexpectedError(self.token)
    def body(self, stat):
        if self.token.type != T.BODY_IN: return None, UnexpectedError(self.token)
        start = self.token.start.copy()
        self.advance()
        statements = []
        while True:
            while self.token.type == T.NL: self.advance()
            statement, err = stat()
            if err: return None, err
            statements.append(statement)
            while self.token.type == T.NL: self.advance()
            if self.token.type == T.BODY_OUT: break
            if self.token.type == T.EOF: return None, ExpectedError(T.BODY_OUT, self.token)
        stop = self.next().stop.copy()
        return BodyNode(statements, start, stop), None
    def parser_body(self):
        if self.token.type != T.BODY_IN: return None, ExpectedError(T.BODY_IN, self.token)
        start = self.token.start.copy()
        self.advance()
        return BodyNode([], start, self.token.stop.copy()), None
    def parse(self):
        start = self.token.start.copy()
        statements = []
        while True:
            while self.token.type == T.NL: self.advance()
            statement, err = self.stat()
            if err: return None, err
            statements.append(statement)
            while self.token.type == T.NL: self.advance()
            if self.token.type == T.EOF: break
        stop = self.next().stop.copy()
        return BodyNode(statements, start, stop), None

def parse(tokens: list):
    parser = Parser(tokens)
    return parser.parse()