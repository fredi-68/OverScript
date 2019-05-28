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

import sys
import pathlib

from compiler import OverScriptCompiler

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: <input script> [output script]")
        raise SystemExit(1)
    p1 = pathlib.Path(sys.argv[1])
    if len(sys.argv) > 2:
        p2 = pathlib.Path(sys.argv[2])
    else:
        p2 = p1.with_suffix(".ow")

    compiler = OverScriptCompiler()
    with open(p1, "r") as file_in:
        with open(p2, "w") as file_out:
            file_out.write(compiler.compile(file_in.read()))

    raise SystemExit(0)