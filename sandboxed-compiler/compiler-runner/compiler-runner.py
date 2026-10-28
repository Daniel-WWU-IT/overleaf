#!/usr/bin/python3
import sys
import re
import os
import unittest
from urllib import request, parse

TESTING = False

INFILE_REGEX = r"^[a-zA-Z0-9/\ _-]+\.tex$"
PC_REGEX = r"^[a-zA-Z0-9\ _-]+$"

HOST = os.environ.get("COMPILE_HOST", "http://127.0.0.1:6666/compile")
COMPILER = ["-pdf", "-pdfdvi", "-lualatex", "-xelatex"]
TIMEOUT = 600


class TestFilepath(unittest.TestCase):
    def test_check_length(self):
        self.assertRaises(PermissionError, check_filepath, "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquy!")

    def test_check_zerodir(self):
        self.assertRaises(PermissionError, check_filepath, "//nope.tex")

    def test_check_folder_symbols(self):
        self.assertRaises(PermissionError, check_filepath, ";rm -rf/main.tex")

    def test_check_vanilla_works(self):
        self.assertEqual(self.mock_check_filepath("main.tex"), "mocked")

    def test_check_folder_works(self):
        self.assertEqual(self.mock_check_filepath("Directory/in/another/main.tex"),
                         "mocked")

    def mock_check_filepath(self, fp):
        check_filepath(fp)
        return "mocked"


def check_filepath(fp):
    if len(fp) > 127:
        raise PermissionError("Please limit total filepath to 127 characters")
    path = fp.split("/")
    for pc in path[:-1]:
        if not re.match(PC_REGEX, pc):
            raise PermissionError("Error: We only support directories with letters, numbers, underscores, hyphens and spaces in the filename before the .tex")
    if not re.match(INFILE_REGEX, path[-1]):
        raise PermissionError("Error: We only support input files with letters, numbers, underscores, hyphens and spaces in the filename before the .tex")


if TESTING:
    unittest.main()
    sys.exit(0)


compiler = ""
infile = ""
auxdir = ""
outdir = ""

for arg in sys.argv:
    if arg.startswith("-auxdir"):
        auxdir = arg[len("-auxdir="):]
    elif arg.startswith("-outdir"):
        outdir = arg[len("-outdir="):]
    elif arg in COMPILER:
        compiler = arg[len("-"):]
    elif arg == sys.argv[-1]:
        infile = arg

args = {
    "compiler" : compiler,
    "infile" : infile,
    "auxdir" : auxdir,
    "outdir" : outdir,
}
infile_without_path = args["infile"][len(args["auxdir"])+1:]

try:
    check_filepath(infile_without_path)
except PermissionError as e:
    with open(args["auxdir"] + "/output.log", "a") as f:
        f.write(f"Error: {e}")
        sys.exit(1)

arg_string = parse.urlencode(args)
with request.urlopen("%s?%s"%(HOST, arg_string), timeout=TIMEOUT) as f:
    print(f.read().decode('utf-8'))
