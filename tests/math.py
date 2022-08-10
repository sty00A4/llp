from main import *

class Math(Interpreter):
    def visit_Int(self, node: dict):
        return int(node["tok"]["value"]), None
    def visit_Float(self, node: dict):
        return float(node["tok"]["value"]), None
    def visit_BinOp(self, node: dict):
        left, err = self.visit(node["left"])
        right, err = self.visit(node["right"])
        if node["op"]['type'].value == "add": return left + right, None
        if node["op"]['type'].value == "sub": return left - right, None
        if node["op"]['type'].value == "mul": return left * right, None
        if node["op"]['type'].value == "div": return left / right, None
        return None, f"unsupported operation '{node['op']['type']}'"

ast = generate("test.llp", "test.math")
math = Math()
value, err = math.visit(ast)
if err: exit(str(err))
print(value)