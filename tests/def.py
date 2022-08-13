from main import *
import rich as r

class Def(Interpreter):
    variables = {}
    def visit_Body(self, node):
        print(r.print(node))
        return None, None


run(Def, "def.llp", "test.def", False)