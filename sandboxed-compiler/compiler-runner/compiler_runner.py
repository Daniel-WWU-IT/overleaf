#!/usr/bin/env python3
import os
import re
import sys
from urllib import request, parse, error


# Various settings can be overridden via environment variables
COMPILER_HOST = os.environ.get("COMPILER_HOST", "http://127.0.0.1:6666/compile")
COMPILERS = ["-pdf", "-pdfdvi", "-lualatex", "-xelatex"]
TIMEOUT = os.environ.get("TIMEOUT", 600)


def _log_error(exc: Exception) -> None:
    with open("/tmp/runner.error.log", "a") as outfile:
        outfile.write(f"Error: {exc}\n")
        sys.exit(1)


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
        _log_error(e)

    args = {
        "compiler": compiler,
        "infile": infile,
        "auxdir": auxdir,
        "outdir": outdir,
    }
    try:
        with request.urlopen(f"{COMPILER_HOST}?{parse.urlencode(args)}", timeout=TIMEOUT) as f:
            output = f.read().decode("utf-8")
            print(output)
    except error.URLError as e:
        _log_error(e)


if __name__ == "__main__":
    launch_compile_pod()
