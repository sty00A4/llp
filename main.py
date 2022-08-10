from src import lexer, parser, transform, llp

class Interpreter:
    def visit(self, node: dict):
        method_name = f"visit_{node['type']}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    def no_visit_method(self, node): raise Exception(f"no visit_{type(node).__name__} method defined")


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

if __name__ == '__main__':
    ast = generate("tests/test.llp", "test.math")
    print(ast)