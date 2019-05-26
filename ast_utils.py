#This utility loads the file ./tests/test.os and parses it into
#an AST, which is then printed to stdout.

import ast

def print_ast(tree, name="root", indent=0):

    print("%s[%s] %s" % ("    "*indent, name, repr(tree)))
    if not isinstance(tree, ast.AST):
        return
    for name, value in ast.iter_fields(tree):
        if not isinstance(value, (list, tuple)):
            value = [value]
        for i in value:
            print_ast(i, name, indent+1)

if __name__ == "__main__":
    with open("tests/test.os", "r") as f:
        tree = ast.parse(f.read())
        print_ast(tree)