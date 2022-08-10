import src.lexer as l
import src.parser as p


class Base:
    def convTree(self, prefix: str = "", subprefix: str = "  "):
        s = f"{self.__class__.__name__}\n"
        attrs = self.__dict__
        for k in attrs:
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

class Name(Base):
    def __init__(self, name: str):
        self.name = name
class Extention(Base):
    def __init__(self, ext: str):
        self.ext = ext

class Token(Base):
    def __init__(self, name: str, strs: list):
        self.name, self.strs = name, strs
class ValueToken(Token):
    def __init__(self, name: str, strs: list):
        super().__init__(name, strs)
class IgnoreToken(Base):
    def __init__(self, strs: list):
        self.strs = strs
class Lexer(Base):
    def __init__(self, tokens: list, ignore: list):
        self.tokens, self.ignore = tokens, ignore

class Layer(Base):
    def __init__(self, name: str, patterns: list, link_layer: str):
        self.name, self.patterns, self.link_layer = name, patterns, link_layer
class Pattern(Base):
    def __init__(self, pattern: list):
        self.pattern = pattern
class Node(Base):
    def __init__(self, name: str, vars_: dict):
        self.name, self.vars = name, vars_
class Group(Base):
    def __init__(self, group: list):
        self.group = group
class Call(Base):
    def __init__(self, name: str, group: Group):
        self.name, self.group = name, group
class To(Base):
    def __init__(self, pattern: Pattern, node: Node):
        self.pattern, self.node = pattern, node
class Parser(Base):
    def __init__(self, layers: list, start_layer: str):
        self.layers, self.start_layer = layers, start_layer

class Language(Base):
    def __init__(self, lexer: Lexer, parser: Parser, name: str = "unnamed", extention=None):
        self.lexer = lexer
        self.parser = parser
        self.name = name
        self.extention = extention

class Transform:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    def no_visit_method(self, node): raise Exception(f"no visit_{type(node).__name__} method defined")
    def visit_NameNode(self, node: p.NameNode) -> str: return node.token.value, None
    def visit_IntNode(self, node: p.IntNode) -> int: return int(node.token.value), None
    def visit_FloatNode(self, node: p.FloatNode) -> float: return float(node.token.value), None
    def visit_GroupNode(self, node: p.GroupNode) -> Group:
        group = []
        for n in node.elements:
            if isinstance(n, l.Token):
                group.append(n)
                continue
            value, err = self.visit(n)
            if err: return None, err
            group.append(value)
        return Group(group), None
    def visit_BodyNode(self, node: p.BodyNode) -> list:
        elements = []
        for n in node.nodes:
            value, err = self.visit(n)
            if err: return None, err
            elements.append(value)
        return elements, None
    def visit_TokenNode(self, node: p.TokenNode) -> Token:
        name = node.name.value
        strs = [n.value for n in node.strs]
        return Token(name, strs), None
    def visit_ValueTokenNode(self, node: p.ValueTokenNode) -> ValueToken:
        name = node.name.value
        strs = [n.value for n in node.strs]
        return ValueToken(name, strs), None
    def visit_IgnoreNode(self, node: p.IgnoreNode) -> ValueToken:
        strs = [n.value for n in node.strs]
        return IgnoreToken(strs), None
    def visit_LexerNode(self, node: p.LexerNode) -> Lexer:
        tokens, err = self.visit(node.body)
        ignores = []
        if err: return None, err
        i = 0
        while i < len(tokens):
            if isinstance(tokens[i], IgnoreToken):
                ignores.extend([s for s in tokens[i].strs])
                tokens.pop(i)
            else:
                i += 1
        return Lexer(tokens, ignores), None
    def visit_CallNode(self, node: p.CallNode) -> Call:
        group, err = self.visit(node.group)
        if err: return None, err
        return Call(node.name.value, group), None
    def visit_PatternNode(self, node: p.PatternNode) -> Pattern:
        pattern = []
        for n in node.elements:
            if isinstance(n, l.Token):
                pattern.append(n)
                continue
            e, err = self.visit(n)
            if err: return None, err
            pattern.append(e)
        return Pattern(pattern), None
    def visit_NodeNode(self, node: p.NodeNode) -> Node:
        name = node.name.value
        vars_ = {}
        for i, v in enumerate(node.vars):
            vars_[v.value], err = self.visit(node.numbers[i])
            if err: return None, err
        return Node(name, vars_), None
    def visit_ToNode(self, node: p.ToNode) -> To:
        node_, err = self.visit(node.node)
        if err: return None, err
        pattern, err = self.visit(node.pattern)
        if err: return None, err
        return To(pattern, node_), None
    def visit_LayerNode(self, node: p.LayerNode) -> Layer:
        patterns, err = self.visit(node.body)
        if err: return None, err
        link_layer = node.link_layer.value
        return Layer(node.name.value, patterns, link_layer), None
    def visit_ParserNode(self, node: p.ParserNode) -> Parser:
        layers, err = self.visit(node.body)
        if err: return None, err
        start_layer = node.start_layer.value
        return Parser(layers, start_layer), None

def transform(body: p.BodyNode) -> Language:
    transform = Transform()
    elements, err = transform.visit(body)
    name, extention, lexer, parser = None, None, None, None
    for v in elements:
        if isinstance(v, Name): name = v.name
        if isinstance(v, Extention): extention = v.ext
        if isinstance(v, Lexer): lexer = v
        if isinstance(v, Parser): parser = v
    return Language(lexer, parser, name, extention), None