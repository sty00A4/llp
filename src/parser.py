from src.lexer import Token, T, Position

class Error:
    def __init__(self, token: Token):
        self.token, self.str = token, "error"
    def __str__(self):
        return f"{self.str} (ln {self.token.start.ln}, col {self.token.start.col})"
class UnexpectedError(Error):
    def __init__(self, token: Token):
        super().__init__(token)
        self.str = f"syntax error: unexpected '{self.token.sub()}' of type {str(self.token.type).lower()[2:]}"
class ExpectedError(Error):
    def __init__(self, expected_type: T, token: Token):
        super().__init__(token)
        self.expected_type = expected_type
        self.str = f"syntax error: expected {str(self.expected_type).lower()[2:]}, got '{self.token.sub()}' of type {str(self.token.type).lower()[2:]}"

class Node:
    def __init__(self, start: Position, stop: Position):
        self.start, self.stop = start, stop
    def __str__(self):
        return repr(self)
class NameNode(Node):
    def __init__(self, token: Token, start: Position):
        super().__init__(start, token.stop)
        self.token = token
    def __repr__(self):
        return f"(NAME {self.token})"
class IntNode(Node):
    def __init__(self, token: Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class FloatNode(Node):
    def __init__(self, token: Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class ExtentionNode(Node):
    def __init__(self, token: Token, start: Position):
        super().__init__(start, token.stop)
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
        return f"(PARSER {self.body} {str(self.start_layer if self.start_layer else '')})"
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
class LayerNode(Node):
    def __init__(self, name: Token, body: BodyNode, link_layer: Token):
        super().__init__(name.start.copy(), body.stop.copy())
        self.name, self.body, self.link_layer = name, body, link_layer
    def __repr__(self):
        return f"(LAYER {self.name} " + " ".join([str(n) for n in self.body.nodes]) + (f" {self.link_layer}" if self.link_layer else "") + ")"
class PatternNode(Node):
    def __init__(self, elements: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.elements = elements
    def __repr__(self):
        return f"(PATTERN " + " ".join([str(n) for n in self.elements]) + ")"
class GroupNode(Node):
    def __init__(self, elements: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.elements = elements
    def __repr__(self):
        return "( " + " ".join([str(n) for n in self.elements]) + " )"
class NodeNode(Node):
    def __init__(self, name: list, vars_: list, numbers: list, start: Position, stop: Position):
        super().__init__(start, stop)
        self.name, self.vars, self.numbers = name, vars_, numbers
    def __repr__(self):
        return f"({self.name} " + " ".join([f"{self.vars[i]}={self.numbers[i]}" for i in range(len(self.vars))]) + ")"
class ToNode(Node):
    def __init__(self, pattern: PatternNode, node: NodeNode):
        super().__init__(pattern.start.copy(), node.stop.copy())
        self.pattern, self.node = pattern, node
    def __repr__(self):
        return f"({self.pattern} -> {self.node})"
class CallNode(Node):
    def __init__(self, name: Token, group: GroupNode):
        super().__init__(name.start.copy(), group.stop.copy())
        self.name, self.group = name, group
    def __repr__(self):
        return f"({self.name} {self.group})"


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
    def lexer_stat(self) -> [ValueTokenNode, IgnoreNode, TokenNode]:
        start = self.token.start.copy()
        if self.token.type == T.VALUE:
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            name = self.next()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next()
                strs.append(string)
            return ValueTokenNode(name, strs, start, stop), None
        if self.token.type == T.IGNORE:
            self.advance()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next()
                strs.append(string)
            return IgnoreNode(strs, start, stop), None
        if self.token.type == T.ID:
            name = self.next()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != T.NL:
                if self.token.type != T.STR: return None, ExpectedError(T.STR, self.token)
                stop = self.token.stop.copy()
                string = self.next()
                strs.append(string)
            return TokenNode(name, strs, start, stop), None
        return None, UnexpectedError(self.token)
    def parser_stat(self) -> LayerNode:
        if self.token.type == T.ID:
            name = self.next()
            link_layer = None
            body, err = self.body(self.layer_stat)
            if err: return None, err
            if self.token.type == T.ID:
                link_layer = self.next()
            if self.token.type != T.NL: return None, UnexpectedError(self.token)
            return LayerNode(name, body, link_layer), None
        return None, ExpectedError(T.ID, self.token)
    def layer_stat(self) -> [PatternNode, ToNode]:
        pattern, err = self.pattern()
        if err: return None, err
        if self.token.type != T.TO: return pattern, None
        self.advance()
        node, err = self.node()
        if err: return None, err
        return ToNode(pattern, node), None
    def node(self) -> [NodeNode, IntNode]:
        if self.token.type == T.INT: return IntNode(self.token), None
        if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
        start, stop = self.token.start.copy(), self.token.stop.copy()
        name = self.next()
        vars_, numbers = [], []
        while self.token.type != T.NL:
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            vars_.append(self.next().copy())
            if self.token.type != T.EQ: return None, ExpectedError(T.EQ, self.token)
            self.advance()
            if self.token.type != T.INT: return None, ExpectedError(T.INT, self.token)
            stop = self.token.stop.copy()
            numbers.append(self.next().copy())
        return NodeNode(name, vars_, numbers, start, stop), None
    def group(self) -> GroupNode:
        if self.token.type != T.GROUP_IN: return None, ExpectedError(T.GROUP_IN, self.token)
        start, stop = self.next().start.copy(), self.token.stop.copy()
        elements = []
        while self.token.type != T.GROUP_OUT:
            if self.token.type == T.GROUP_IN:
                group, err = self.group()
                if err: return None, err
                stop = group.stop.copy()
                elements.append(group)
                continue
            stop = self.token.stop.copy()
            elements.append(self.next())
        self.advance()
        return GroupNode(elements, start, stop), None
    def pattern(self) -> PatternNode:
        tokens = [T.ID, T.TOKEN, T.BINARY, T.GROUP_IN]
        pattern = []
        #if self.token.type == T.EQ: raise Exception("here")
        if self.token.type not in tokens: return None, UnexpectedError(self.token)
        start = self.token.start.copy()
        stop = self.token.stop.copy()
        while self.token.type in tokens:
            if self.token.type in [T.BINARY]:
                name = self.token.copy()
                self.advance()
                group, err = self.group()
                if err: return None, err
                stop = group.stop.copy()
                pattern.append(CallNode(name, group))
                continue
            if self.token.type == T.GROUP_IN:
                group, err = self.group()
                if err: return None, err
                pattern.append(group)
                continue
            stop = self.token.stop.copy()
            pattern.append(self.next())
        return PatternNode(pattern, start, stop), None
    def stat(self):
        if self.token.type == T.NAME:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            return NameNode(self.next(), start), None
        if self.token.type == T.EXTENTION:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != T.ID: return None, ExpectedError(T.ID, self.token)
            return ExtentionNode(self.next(), start), None
        if self.token.type == T.LEXER:
            start = self.token.start.copy()
            self.advance()
            body, err = self.body(self.lexer_stat)
            if err: return None, err
            return LexerNode(body, start, body.stop.copy()), None
        if self.token.type == T.PARSER:
            start = self.next().start.copy()
            start_layer = None
            body, err = self.body(self.parser_stat)
            if err: return None, err
            if self.token.type == T.ID:
                start_layer = self.next()
            return ParserNode(body, start_layer, start, body.stop.copy()), None
        return None, UnexpectedError(self.token)
    def body(self, stat) -> BodyNode:
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