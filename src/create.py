import src.lexer as l
import src.parser as p

class Match:
    pass

class Lexer:
    pass

class Layer:
    pass

class Pattern:
    pass

class Node:
    pass

class Parser:
    pass

class Language:
    def __init__(self, lexer: Lexer, parser: Parser, name: str = "unnamed", extention = None):
        self.lexer = lexer
        self.parser = parser
        self.name = name
        self.extention = extention

def create(body: p.BodyNode) -> Language:
    return Language(Lexer(), Parser()), None