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
import argparse
import logging
import os

SUFFIX_INPUT = (".os", ".py", ".pyos")
SUFFIX_OUTPUT = (".ows",) #winner of the great 2019 overwatch workshop rule file extension vote (not representative)

log_levels = {
    0: logging.WARN,
    1: logging.INFO,
    2: logging.DEBUG
    }

from compiler import OverScriptCompiler

parser = argparse.ArgumentParser(description="CLI for the OverScript compiler")
parser.add_argument("-v", "--verbose", action="count", default=0, help="Set logging level")
parser.add_argument("-o", "--out", action="store", help="Set output file path")
parser.add_argument("-O", "--optimize", action="store_true", help="optimize output")
parser.add_argument("-g", "--guess", action="store_true", help="attempt to guess unknown functions instead of raising error")
parser.add_argument("-c", "--correct-accents", action="store_true", help="use text filters to correct common misspellings of string literals")
parser.add_argument("source", nargs="+")

args = parser.parse_args()
if args.verbose in log_levels:
    logging.basicConfig(level=log_levels[args.verbose])
else:
    logging.basicConfig(level=logging.DEBUG)

p_in = args.source
compiler = OverScriptCompiler(optimize=args.optimize, parseUnknownFunctions=args.guess, correctAccents=args.correct_accents)
for i in p_in:
    path = pathlib.Path(i)
    if not path.exists():
        logging.error("File '%s' does not exist, skipping..." % str(path))
        continue
    if args.out:
        target = pathlib.Path(args.out)
        os.makedirs(target, exist_ok=True)
    else:
        target = path.parent
    filename = path.stem + SUFFIX_OUTPUT[0]
    p = target / filename
    logging.info("Compiling file '%s'..." % str(path))
    with open(path, "r") as file_in:
        with open(p, "w") as file_out:
            file_out.write(compiler.compile(file_in.read()))