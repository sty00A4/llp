from src import lexer, parser, transform, llp

class Interpreter:
    def visit(self, node: dict):
        if type(node) is not dict: exit(f"cannot visit node of type {type(node).__name__}")
        method_name = f"visit_{node['type']}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    def no_visit_method(self, node):
        exit(f"no visit_{node['type']} method defined in interpreter")
    def enter(self, node):
        return self.visit(node)

def generate(llp_fn: str, fn: str, debug: bool = False) -> dict:
    with open(llp_fn, "r") as f:
        tokens, err = lexer.tokenize(llp_fn, f.read())
        if err: exit(str(err))
        # for tok in tokens: print(tok)
        body, err = parser.parse(tokens)
        if err: exit(str(err))
        # print(body)
        lang, err = transform.transform(body)
        if err: exit(str(err))
        # print(language.convTree("", ". "))
        ast, err = llp.from_file(fn, lang, debug)
        if err: exit(str(err))
        return ast

def run(interpreter, llp_fn: str, fn: str, debug: bool = False):
    ast = generate(llp_fn, fn, debug)
    math = interpreter()
    out = math.enter(ast)
    if out[-1]: exit(str(out[-1]))
    if out[0] is not None: print(out[0])


if __name__ == '__main__':
    ast = generate("tests/math.llp", "test.math")
    print(ast)