import src.lexer as l
import src.parser as p


class Base:
    def __init__(self, start: l.Position, stop: l.Position):
        self.start, self.stop = start, stop
    def convTree(self, prefix: str = "", subprefix: str = "  "):
        s = f"{self.__class__.__name__}\n"
        attrs = self.__dict__
        for k in attrs:
            if k in ["start", "stop"]: continue
            if getattr(attrs[k], "convTree", False): s += f"{prefix}{k}: {attrs[k].convTree(prefix+subprefix, subprefix)}"
            elif type(attrs[k]) is list: s += f"{prefix}{k}:\n{self.convList(attrs[k], prefix+subprefix, subprefix)}"
            else: s += f"{prefix}{k}: {repr(attrs[k])}"
            s += "\n"
        return s[:-1]
    def convList(self, l, prefix: str = "", subprefix: str = "  "):
        s = ""
        for v in l:
            if getattr(v, "convTree", False): s += f"{prefix}{v.convTree(prefix + subprefix, subprefix)}"
            elif type(v) is list: s += f"{prefix}\n{self.convList(v, prefix+subprefix, subprefix)}"
            else: s += f"{prefix}{repr(v)}"
            s += "\n"
        return s[:-1]
    def __str__(self):
        return self.convTree("  ")
    def __repr__(self):
        return str(self)

class Int(Base):
    def __init__(self, value: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.value = int(value)
    def __str__(self):
        return repr(self.value)
class Float(Base):
    def __init__(self, value: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.value = float(value)
    def __str__(self):
        return repr(self.value)
class String(Base):
    def __init__(self, value: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.value = value
    def __str__(self):
        return repr(self.value)
class ID(Base):
    def __init__(self, value: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.value = value
    def __str__(self):
        return self.value
class Var(Base):
    def __init__(self, value: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.value = value
    def __str__(self):
        return self.value
class Token(Base):
    def __init__(self, type: str, value, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.type, self.value = type, value
    def __str__(self):
        return f"[{self.type}{f':{self.value}' if self.value is not None else ''}]"
class Name(Base):
    def __init__(self, name: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name = name
class Extention(Base):
    def __init__(self, ext: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.ext = ext

class TokenMatch(Base):
    def __init__(self, name: str, strs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.strs = name, strs
class ValueToken(TokenMatch):
    def __init__(self, name: str, strs: list, start: l.Position, stop: l.Position):
        super().__init__(name, strs, start, stop)
class IgnoreToken(Base):
    def __init__(self, strs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.strs = strs
class Lexer(Base):
    def __init__(self, tokens: list, ignore: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.tokens, self.ignore = tokens, ignore

class Layer(Base):
    def __init__(self, name: str, patterns: list, link_layer: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.patterns, self.link_layer = name, patterns, link_layer
class Pattern(Base):
    def __init__(self, pattern: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.pattern = pattern
class Node(Base):
    def __init__(self, name: ID, vars_: dict, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.vars = name, vars_
class Group(Base):
    def __init__(self, group: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.group = group
    def __str__(self):
        return f"({' '.join([f'{e}' for e in self.group])})"
class Repeat(Base):
    def __init__(self, node, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.node = node
    def __str__(self):
        return f"({self.node} *)"
class Binary(Base):
    def __init__(self, group: Group, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.left = group.group[0]
        self.op = group.group[1]
        self.right = group.group[2] if len(group.group) >= 3 else group.group[0]
    def __str__(self):
        return f"(BINARY {self.left} {self.op} {self.right})"
class To(Base):
    def __init__(self, pattern: Pattern, node: Node, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.pattern, self.node = pattern, node
    def __str__(self):
        return f"({self.pattern} -> {self.node})"
class Parser(Base):
    def __init__(self, layers: list, start_layer: str, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.layers, self.start_layer = layers, start_layer
    def get_layer(self, name: ID):
        for layer in self.layers:
            if name.value == layer.name.value: return layer

class ErrorCall(Base):
    def __init__(self, name: ID, args: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.name, self.args = name, args
    def __str__(self):
        return f"(ERROR ({' '.join([f'{e}' for e in self.args])}) )"
class ErrorDef(Base):
    def __init__(self, name: ID, s: String):
        super().__init__(name.start, s.stop)
        self.name, self.str = name, s
    def __str__(self):
        return f"({self.name} {self.str})"
class Error(Base):
    def __init__(self, defs: list, start: l.Position, stop: l.Position):
        super().__init__(start, stop)
        self.defs = defs
    def get_def(self, name: ID):
        for defin in self.defs:
            if name.value == defin.name.value: return defin

class Language(Base):
    def __init__(self, lexer: Lexer, parser: Parser, error: Error, name: str = "unnamed", extention=None):
        stop = lexer.stop
        if parser: stop = parser.stop
        if error: stop = error.stop
        super().__init__(lexer.start, stop)
        self.lexer = lexer
        self.parser = parser
        self.error = error
        self.name = name
        self.extention = extention

class Transform:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    def no_visit_method(self, node): raise Exception(f"no visit_{type(node).__name__} method defined")
    def visit_NameNode(self, node: p.NameNode) -> Name: return Name(node.token.value, node.start, node.stop), None
    def visit_IntNode(self, node: p.IntNode) -> Int: return Int(node.token.value, node.start, node.stop), None
    def visit_FloatNode(self, node: p.FloatNode) -> Float: return Float(node.token.value, node.start, node.stop), None
    def visit_StringNode(self, node: p.StringNode) -> String: return String(node.token.value, node.start, node.stop), None
    def visit_IDNode(self, node: p.IDNode) -> ID: return ID(node.token.value, node.start, node.stop), None
    def visit_VarNode(self, node: p.VarNode) -> Var:
        return Var(node.token.value, node.start, node.stop), None
    def visit_TokenNode(self, node: p.TokenNode) -> Token:
        return Token(node.type, node.value, node.start, node.stop), None
    def visit_GroupNode(self, node: p.GroupNode) -> Group:
        group = []
        for n in node.elements:
            if isinstance(n, l.Token):
                group.append(n)
                continue
            value, err = self.visit(n)
            if err: return None, err
            group.append(value)
        return Group(group, node.start, node.stop), None
    def visit_BodyNode(self, node: p.BodyNode) -> list:
        elements = []
        for n in node.nodes:
            value, err = self.visit(n)
            if err: return None, err
            elements.append(value)
        return elements, None
    def visit_TokenMatchNode(self, node: p.TokenMatchNode) -> TokenMatch:
        name, err = self.visit(node.name)
        strs = []
        for n in node.strs:
            value, err = self.visit(n)
            if err: return None, err
            strs.append(value)
        return TokenMatch(name, strs, node.start, node.stop), None
    def visit_ValueTokenNode(self, node: p.ValueTokenNode) -> ValueToken:
        name, err = self.visit(node.name)
        if err: return None, err
        strs = []
        for n in node.strs:
            value, err = self.visit(n)
            if err: return None, err
            strs.append(value)
        return ValueToken(name, strs, node.start, node.stop), None
    def visit_IgnoreNode(self, node: p.IgnoreNode) -> ValueToken:
        strs = []
        for n in node.strs:
            value, err = self.visit(n)
            if err: return None, err
            strs.append(value)
        return IgnoreToken(strs, node.start, node.stop), None
    def visit_LexerNode(self, node: p.LexerNode) -> Lexer:
        tokens, err = self.visit(node.body)
        if err: return None, err
        ignores = []
        i = 0
        while i < len(tokens):
            if isinstance(tokens[i], IgnoreToken):
                ignores.extend(tokens[i].strs)
                tokens.pop(i)
            else:
                i += 1
        return Lexer(tokens, ignores, node.start, node.stop), None
    def visit_BinaryNode(self, node: p.BinaryNode) -> Binary:
        group, err = self.visit(node.group)
        if err: return None, err
        return Binary(group, node.start, node.stop), None
    def visit_PatternNode(self, node: p.PatternNode) -> Pattern:
        pattern = []
        for n in node.elements:
            if n is None: continue
            if isinstance(n, l.Token):
                pattern.append(n)
                continue
            e, err = self.visit(n)
            if err: return None, err
            pattern.append(e)
        return Pattern(pattern, node.start, node.stop), None
    def visit_RepeatNode(self, node: p.RepeatNode) -> Repeat:
        node, err = self.visit(node.node)
        if err: return None, err
        return Repeat(node, node.start, node.stop), None
    def visit_NodeNode(self, node: p.NodeNode) -> Node:
        name, err = self.visit(node.name)
        if err: return None, err
        vars_ = {}
        for i, v in enumerate(node.vars):
            vars_[v.token.value], err = self.visit(node.numbers[i])
            if err: return None, err
        return Node(name, vars_, node.start, node.stop), None
    def visit_ToNode(self, node: p.ToNode) -> To:
        node_, err = self.visit(node.node)
        if err: return None, err
        pattern, err = self.visit(node.pattern)
        if err: return None, err
        return To(pattern, node_, node.start, node.stop), None
    def visit_ErrorCallNode(self, node: p.ErrorCallNode) -> ErrorCall:
        name, err = self.visit(node.name)
        if err: return None, err
        args = []
        for n in node.args:
            arg, err = self.visit(n)
            if err: return None, err
            args.append(arg)
        return ErrorCall(name, args, node.start, node.stop), None
    def visit_ErrorDefNode(self, node: p.ErrorDefNode) -> ErrorDef:
        name, err = self.visit(node.name)
        if err: return None, err
        s, err = self.visit(node.str)
        if err: return None, err
        return ErrorDef(name, s), None
    def visit_LayerNode(self, node: p.LayerNode) -> Layer:
        patterns, err = self.visit(node.body)
        if err: return None, err
        link_layer, err = self.visit(node.link_layer) if node.link_layer else (None, None)
        if err: return None, err
        name, err = self.visit(node.name)
        if err: return None, err
        return Layer(name, patterns, link_layer, node.start, node.stop), None
    def visit_ParserNode(self, node: p.ParserNode) -> Parser:
        layers, err = self.visit(node.body)
        if err: return None, err
        start_layer, err = self.visit(node.start_layer)
        if err: return None, err
        return Parser(layers, start_layer, node.start, node.stop), None
    def visit_ErrorNode(self, node: p.ErrorNode) -> Error:
        body, err = self.visit(node.body)
        if err: return None, err
        return Error(body, node.start, node.stop), None

def transform(body: p.BodyNode) -> Language:
    transform = Transform()
    elements, err = transform.visit(body)
    name, extention, lexer, parser, error = None, None, None, None, None
    for v in elements:
        if isinstance(v, Name): name = v.name
        if isinstance(v, Extention): extention = v.ext
        if isinstance(v, Lexer): lexer = v
        if isinstance(v, Parser): parser = v
        if isinstance(v, Error): error = v
    return Language(lexer, parser, error, name, extention), None