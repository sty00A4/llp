from main import *

class Math(Interpreter):
    def visit_Int(self, node: dict):
        return int(node["tok"]["value"]), None
    def visit_Float(self, node: dict):
        return float(node["tok"]["value"]), None
    def visit_BinaryOperation(self, node: dict):
        left, err = self.visit(node["left"])
        if err: return None, err
        right, err = self.visit(node["right"])
        if err: return None, err
        if node["op"]['type'].value == "add": return left + right, None
        if node["op"]['type'].value == "sub": return left - right, None
        if node["op"]['type'].value == "mul": return left * right, None
        if node["op"]['type'].value == "div": return left / right, None
        return None, f"unsupported binary operation '{node['op']['type']}'"
    def visit_UnaryOperation(self, node: dict):
        value, err = self.visit(node["node"])
        if err: return None, err
        if node["op"]['type'].value == "add": return value, None
        if node["op"]['type'].value == "sub": return -value, None
        return None, f"unsupported unary operation '{node['op']['type']}'"

run(Math, "math.llp", "test.math")