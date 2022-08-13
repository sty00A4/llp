import src.lexer as l

class Error:
    def __init__(self, token: l.Token):
        self.token, self.str = token, "error"
    def __str__(self):
        return f"{self.str} (ln {self.token.start.ln}, col {self.token.start.col})"
class UnexpectedError(Error):
    def __init__(self, token: l.Token):
        super().__init__(token)
        self.str = f"syntax error: unexpected '{self.token.sub()}' of type {str(self.token.type).lower()[2:]}"
class ExpectedError(Error):
    def __init__(self, expected_type: l.T, token: l.Token):
        super().__init__(token)
        self.expected_type = expected_type
        self.str = f"syntax error: expected {str(self.expected_type).lower()[2:]}, got '{self.token.sub()}' of type {str(self.token.type).lower()[2:]}"

class Node:
    def __init__(self, start: l.Position, stop: l.Position):
        self.start, self.stop = start, stop
    def __str__(self):
        return repr(self)
class NameNode(Node):
    def __init__(self, token: l.Token, start: l.Position):
        super().__init__(start, token.stop)
        self.token = token
    def __repr__(self):
        return f"(NAME {self.token})"
class IntNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class StringNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class FloatNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class IDNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"({self.token})"
class VarNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.token = token
    def __repr__(self):
        return f"(@{self.token})"
class TokenNode(Node):
    def __init__(self, token: l.Token):
        super().__init__(token.start, token.stop)
        self.type = token.type
        self.value = token.value
    def __repr__(self):
        return f"([{self.type}{f':{self.value}' if self.value is not None else ''}])"

class ExtentionNode(Node):
    def __init__(self, token: l.Token, start: l.Position):
        super().__init__(start, token.stop)
        self.token = token
    def __repr__(self):
        return f"(EXTENTION {self.token})"
class BodyNode(Node):
    def __init__(self, nodes: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.nodes = nodes
    def __repr__(self):
        return "({\n" + "\n".join([str(n) for n in self.nodes]) + "\n})"
class LexerNode(Node):
    def __init__(self, body: BodyNode, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.body = body
    def __repr__(self):
        return f"(LEXER {self.body})"
class ParserNode(Node):
    def __init__(self, body: BodyNode, start_layer: l.Token, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.body = body
        self.start_layer = start_layer
    def __repr__(self):
        return f"(PARSER {self.body} {str(self.start_layer if self.start_layer else '')})"
class ErrorNode(Node):
    def __init__(self, body: BodyNode, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.body = body
    def __repr__(self):
        return f"(ERROR {self.body})"
class ErrorDefNode(Node):
    def __init__(self, name: BodyNode, s: StringNode):
        super().__init__(name.start, s.stop)
        self.name, self.str = name, s
    def __repr__(self):
        return f"({self.name} {self.str})"
class ValueTokenNode(Node):
    def __init__(self, name: l.Token, strs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.strs = name, strs
    def __repr__(self):
        return f"(VALUE {self.name} " + " ".join([str(n) for n in self.strs]) + ")"
class TokenMatchNode(Node):
    def __init__(self, name: l.Token, strs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.strs = name, strs
    def __repr__(self):
        return f"({self.name} " + " ".join([str(n) for n in self.strs]) + ")"
class IgnoreNode(Node):
    def __init__(self, strs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.strs = strs
    def __repr__(self):
        return f"(IGNORE " + " ".join([str(n) for n in self.strs]) + ")"
class LayerNode(Node):
    def __init__(self, name: l.Token, body: BodyNode, link_layer: l.Token):
        super().__init__(name.start.copy(), body.stop.copy())
        self.name, self.body, self.link_layer = name, body, link_layer
    def __repr__(self):
        return f"(LAYER {self.name} " + " ".join([str(n) for n in self.body.nodes]) + (f" {self.link_layer}" if self.link_layer else "") + ")"
class PatternNode(Node):
    def __init__(self, elements: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.elements = elements
    def __repr__(self):
        return f"(PATTERN " + " ".join([str(n) for n in self.elements]) + ")"
class GroupNode(Node):
    def __init__(self, elements: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.elements = elements
    def __repr__(self):
        return "( " + " ".join([str(n) for n in self.elements]) + " )"
class RepeatNode(Node):
    def __init__(self, node, stop: l.Position):
        super().__init__(node.start, stop)
        self.node = node
    def __repr__(self):
        return f"({self.node} *)"
class NodeNode(Node):
    def __init__(self, name: l.Token, vars_: list, numbers: list, start: l.Position, stop: l.Position):
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
    def __init__(self, name: l.Token, group: GroupNode):
        super().__init__(name.start.copy(), group.stop.copy())
        self.name, self.group = name, group
    def __repr__(self):
        return f"({self.name} {self.group})"
class ErrorCallNode(Node):
    def __init__(self, name: l.Token, args: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.args = name, args
    def __repr__(self):
        return f"(ERROR {self.name} " + " ".join([str(n) for n in self.args]) + ")"
class BinaryNode(Node):
    def __init__(self, group: GroupNode, start: l.Position):
        super().__init__(start, group.stop)
        self.group = group
    def __repr__(self):
        return f"(BINARY {self.group})"


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.token: l.Token = tokens[0]
        self.idx = 0
    def advance(self):
        self.idx += 1
        if self.idx >= len(self.tokens): self.idx = len(self.tokens) - 1
        self.token: l.Token = self.tokens[self.idx]
    def next(self) -> l.Token:
        token: l.Token = self.token.copy()
        self.advance()
        return token
    def translate(self, token: l.Token):
        if token.type == l.T.TOKEN: return TokenNode(token)
        if token.type == l.T.ID: return IDNode(token)
        if token.type == l.T.VAR: return VarNode(token)
        if token.type == l.T.STR: return StringNode(token)
        if token.type == l.T.INT: return IntNode(token)
        if token.type == l.T.FLOAT: return FloatNode(token)
    def lexer_stat(self) -> [ValueTokenNode, IgnoreNode, TokenMatchNode]:
        start = self.token.start.copy()
        if self.token.type == l.T.VALUE:
            self.advance()
            if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
            name = IDNode(self.next())
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != l.T.NL:
                if self.token.type != l.T.STR: return None, ExpectedError(l.T.STR, self.token)
                stop = self.token.stop.copy()
                string = StringNode(self.next())
                strs.append(string)
            return ValueTokenNode(name, strs, start, stop), None
        if self.token.type == l.T.IGNORE:
            self.advance()
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != l.T.NL:
                if self.token.type != l.T.STR: return None, ExpectedError(l.T.STR, self.token)
                stop = self.token.stop.copy()
                string = StringNode(self.next())
                strs.append(string)
            return IgnoreNode(strs, start, stop), None
        if self.token.type == l.T.ID:
            name = IDNode(self.next())
            strs = []
            stop = self.token.stop.copy()
            while self.token.type != l.T.NL:
                if self.token.type != l.T.STR: return None, ExpectedError(l.T.STR, self.token)
                stop = self.token.stop.copy()
                string = StringNode(self.next())
                strs.append(string)
            return TokenMatchNode(name, strs, start, stop), None
        return None, UnexpectedError(self.token)
    def parser_stat(self) -> LayerNode:
        if self.token.type == l.T.ID:
            name = IDNode(self.next())
            link_layer = None
            body, err = self.body(self.layer_stat)
            if err: return None, err
            if self.token.type == l.T.ID:
                link_layer = IDNode(self.next())
            if self.token.type == l.T.ERROR:
                start, stop = self.next().start.copy(), self.token.stop.copy()
                if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
                error_name = IDNode(self.next())
                args = []
                while self.token.type != l.T.NL:
                    stop = self.token.stop.copy()
                    token = self.translate(self.next())
                    if err: return None, err
                    args.append(token)
                link_layer = ErrorCallNode(error_name, args, start, stop)
            if self.token.type != l.T.NL: return None, UnexpectedError(self.token)
            return LayerNode(name, body, link_layer), None
        return None, ExpectedError(l.T.ID, self.token)
    def layer_stat(self) -> [PatternNode, ToNode]:
        pattern, err = self.pattern()
        if err: return None, err
        if self.token.type != l.T.TO: return pattern, None
        self.advance()
        node, err = self.node()
        if err: return None, err
        return ToNode(pattern, node), None
    def node(self) -> [NodeNode, IntNode]:
        if self.token.type not in [l.T.ID, l.T.INT]: return None, ExpectedError(l.T.ID, self.token)
        start, stop = self.token.start.copy(), self.token.stop.copy()
        name = self.translate(self.next())
        vars_, numbers = [], []
        while self.token.type != l.T.NL:
            if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
            vars_.append(IDNode(self.next().copy()))
            if self.token.type != l.T.EQ: return None, ExpectedError(l.T.EQ, self.token)
            self.advance()
            if self.token.type != l.T.INT: return None, ExpectedError(l.T.INT, self.token)
            stop = self.token.stop.copy()
            numbers.append(IntNode(self.next().copy()))
        return NodeNode(name, vars_, numbers, start, stop), None
    def group(self) -> GroupNode:
        if self.token.type != l.T.GROUP_IN: return None, ExpectedError(l.T.GROUP_IN, self.token)
        start, stop = self.next().start.copy(), self.token.stop.copy()
        elements = []
        while self.token.type != l.T.GROUP_OUT:
            if self.token.type == l.T.GROUP_IN:
                group, err = self.group()
                if err: return None, err
                stop = group.stop.copy()
                elements.append(group)
                continue
            stop = self.token.stop.copy()
            elements.append(self.translate(self.next()))
        self.advance()
        return GroupNode(elements, start, stop), None
    def pattern(self) -> PatternNode:
        tokens = [l.T.ID, l.T.TOKEN, l.T.GROUP_IN, l.T.BINARY, l.T.REPEAT]
        pattern = []
        if self.token.type not in tokens: return None, UnexpectedError(self.token)
        start = self.token.start.copy()
        stop = self.token.stop.copy()
        while self.token.type in tokens:
            if self.token.type == l.T.GROUP_IN:
                group, err = self.group()
                if err: return None, err
                pattern.append(group)
                continue
            if self.token.type == l.T.BINARY:
                start = self.token.start.copy()
                self.advance()
                group, err = self.group()
                if err: return None, err
                pattern.append(BinaryNode(group, start))
                continue
            if self.token.type == l.T.REPEAT:
                stop = self.token.stop.copy()
                self.advance()
                pattern[-1] = RepeatNode(pattern[-1], stop)
                continue
            stop = self.token.stop.copy()
            pattern.append(self.translate(self.next()))
        return PatternNode(pattern, start, stop), None
    def error_stat(self) -> ErrorDefNode:
        if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
        name = IDNode(self.next())
        if self.token.type != l.T.STR: return None, ExpectedError(l.T.STR, self.token)
        s = StringNode(self.next())
        return ErrorDefNode(name, s), None
    def stat(self):
        if self.token.type == l.T.NAME:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
            return NameNode(self.next(), start), None
        if self.token.type == l.T.EXTENTION:
            start = self.token.start.copy()
            self.advance()
            if self.token.type != l.T.ID: return None, ExpectedError(l.T.ID, self.token)
            return ExtentionNode(self.next(), start), None
        if self.token.type == l.T.LEXER:
            start = self.token.start.copy()
            self.advance()
            body, err = self.body(self.lexer_stat)
            if err: return None, err
            return LexerNode(body, start, body.stop.copy()), None
        if self.token.type == l.T.PARSER:
            start = self.next().start.copy()
            start_layer = None
            body, err = self.body(self.parser_stat)
            if err: return None, err
            if self.token.type == l.T.ID:
                start_layer = IDNode(self.next())
            return ParserNode(body, start_layer, start, body.stop.copy()), None
        if self.token.type == l.T.ERROR:
            start = self.next().start.copy()
            body, err = self.body(self.error_stat)
            if err: return None, err
            return ErrorNode(body, start, body.stop.copy()), None
        return None, UnexpectedError(self.token)
    def body(self, stat) -> BodyNode:
        if self.token.type != l.T.BODY_IN: return None, UnexpectedError(self.token)
        start = self.token.start.copy()
        self.advance()
        statements = []
        while True:
            while self.token.type == l.T.NL: self.advance()
            statement, err = stat()
            if err: return None, err
            statements.append(statement)
            while self.token.type == l.T.NL: self.advance()
            if self.token.type == l.T.BODY_OUT: break
            if self.token.type == l.T.EOF: return None, ExpectedError(l.T.BODY_OUT, self.token)
        stop = self.next().stop.copy()
        return BodyNode(statements, start, stop), None
    def parse(self):
        start = self.token.start.copy()
        statements = []
        while True:
            while self.token.type == l.T.NL: self.advance()
            statement, err = self.stat()
            if err: return None, err
            statements.append(statement)
            while self.token.type == l.T.NL: self.advance()
            if self.token.type == l.T.EOF: break
        stop = self.next().stop.copy()
        return BodyNode(statements, start, stop), None

def parse(tokens: list):
    parser = Parser(tokens)
    return parser.parse()