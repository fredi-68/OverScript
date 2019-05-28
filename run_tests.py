#This utility takes all files from the ./tests directory ending in .os (OverScript)
#and compiles them into .ow (OverWatch workshop script) files which may be
#imported into the Overwatch Workshop

from compiler import OverScriptCompiler
import pathlib
import logging

if __debug__:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logging.info("Compiling test scripts...")
comp = OverScriptCompiler()
for file in pathlib.Path("./tests").iterdir():
    if file.suffix == ".os":
        logging.info("Compiling script '%s'..." % str(file))
        with open(file, "r") as f_in:
            with open(file.with_suffix(".ow"), "w") as f_out:
                f_out.write(comp.compile(f_in.read()))