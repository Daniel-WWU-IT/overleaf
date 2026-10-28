#!/usr/bin/env python3
import os
import re
import sys
from urllib import request, parse


# Various settings can be overridden via environment variables
COMPILEHOST = os.environ.get("COMPILER_RUNNER_HOST", "http://127.0.0.1:6666/compile")
COMPILERS = ["-pdf", "-pdfdvi", "-lualatex", "-xelatex"]
TIMEOUT = os.environ.get("COMPILER_RUNNER_TIMEOUT", 600)


def _check_filepath(fp: str) -> None:
    if len(fp) > 127:
        raise PermissionError("Please limit the total filepath length to 127 characters")
    path = fp.split("/")
    for pc in path[:-1]:
        if not re.match(r"^[a-zA-Z0-9 _-]+$", pc):
            raise PermissionError("Filepaths may only contain letters, numbers, underscores, hyphens and spaces")
    if not re.match(r"^[a-zA-Z0-9 _-]+\.tex$", path[-1]):
        raise PermissionError("Filepaths may only contain letters, numbers, underscores, hyphens and spaces")


def launch_compile_pod() -> None:
    compiler = ""
    infile = ""
    auxdir = ""
    outdir = ""
    for arg in sys.argv:
        if arg.startswith("-auxdir"):
            auxdir = arg[len("-auxdir="):]
        elif arg.startswith("-outdir"):
            outdir = arg[len("-outdir="):]
        elif arg in COMPILERS:
            compiler = arg[len("-"):]
        elif arg == sys.argv[-1]:
            infile = arg
    try:
        _check_filepath(infile[len(auxdir) + 1:])
    except PermissionError as e:
        with open(auxdir + "/output.log", "a") as f:
            f.write(f"Error: {e}")
            sys.exit(1)

    args = {
        "compiler": compiler,
        "infile": infile,
        "auxdir": auxdir,
        "outdir": outdir,
    }
    with request.urlopen(f"{COMPILEHOST}?{parse.urlencode(args)}", timeout=TIMEOUT) as f:
        print(f.read().decode("utf-8"))


if __name__ == "__main__":
    launch_compile_pod()
