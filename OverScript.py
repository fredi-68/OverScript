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