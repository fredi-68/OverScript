#This utility loads the file ./tests/test.os and parses it into
#an AST, which is then printed to stdout.

#Copyright (c) 2019 fredi_68

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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