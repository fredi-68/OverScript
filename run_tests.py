#This utility takes all files from the ./tests directory ending in .os (OverScript)
#and compiles them into .ow (OverWatch workshop script) files which may be
#imported into the Overwatch Workshop

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

from compiler import OverScriptCompiler
import pathlib
import logging

if __debug__:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logging.info("Compiling test scripts...")
comp = OverScriptCompiler(parseUnknownFunctions=False)
for file in pathlib.Path("./tests").iterdir():
    if file.suffix == ".os":
        logging.info("Compiling script '%s'..." % str(file))
        with open(file, "r") as f_in:
            with open(file.with_suffix(".ows"), "w") as f_out:
                f_out.write(comp.compile(f_in.read()))