from main import *

class Def(Interpreter):
    variables = {}
    types = {}
    def visit_Id(self, node):
        name = node['tok']['value']
        if name in self.variables:
            return self.variables[name], False, None
        return None, False, f"variable {name} not defined"
    def visit_Int(self, node):
        return int(node['tok']['value']), False, None
    def visit_Float(self, node):
        return float(node['tok']['value']), False, None
    def visit_Print(self, node):
        value, _, err = self.visit(node['node'])
        if err: return None, False, err
        print(value)
        return None, False, None
    def visit_Definition(self, node):
        name = node['name']['tok']['value']
        self.variables[name] = node['body']
        self.types[name] = "procedure"
        return None, False, None
    def visit_Body(self, node):
        for n in node['body']:
            value, returning, err = self.visit(n)
            if err: return None, False, err
            if returning: return value, returning, err
        return None, False, None
    def enter(self, node):
        _, _, err = self.visit(node)
        if 'main' not in self.variables: return None, False, 'no main function'
        return self.visit(self.variables['main'])

run(Def, 'def.llp', 'test.def', False)