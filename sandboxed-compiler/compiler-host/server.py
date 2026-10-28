#!/usr/bin/env python3

from flask import Flask, request, redirect
from time import sleep
import unittest
import os
import pprint
import subprocess
import re

# latex commands look like this:
# latexmk -cd -jobname=output -auxdir=/var/lib/sharelatex/data/compiles/67dbe26e588f6f00a1dfbf22-671b49b29b04a8171df57c5d -outdir=/var/lib/sharelatex/data/compiles/67dbe26e588f6f00a1dfbf22-671b49b29b04a8171df57c5d -synctex=1 -interaction=batchmode -f -xelatex /var/lib/sharelatex/data/compiles/67dbe26e588f6f00a1dfbf22-671b49b29b04a8171df57c5d/script.tex

TEXLIVE_IMAGE = os.environ.get('TEXLIVE_IMAGE',
                               'docker.io/texlive/texlive:TL2024-historic')
UID = os.environ.get('SHARELATEX_UID', '33')
GID = os.environ.get('SHARELATEX_UID', '33')
TIMEOUT = os.environ.get("COMPILE_TIMEOUT", 600)
INFILE_REGEX = r"^[a-zA-Z0-9\ _-]+\.tex$"
PC_REGEX = r"^[a-zA-Z0-9\ _-]+$"

# We need to keep directories the same or fiddle around with the synctex file
CMD_TEMPLATE = "timeout {timeout} podman run"
CMD_TEMPLATE += " -u{uid}:{gid} -v {auxdir}:{auxdir} -w {auxdir}"
CMD_TEMPLATE += " --rm --network=none {image} {command}"
# CMD_TEMPLATE="timeout {timeout} podman run -u{uid}:{gid} -v {auxdir}:/mnt --rm --network=none {image} {command}"
LATEX_COMMAND_TEMPLATE = 'latexmk -cd -jobname=output'
LATEX_COMMAND_TEMPLATE += ' -auxdir={auxdir} -outdir={outdir} -synctex=1'
LATEX_COMMAND_TEMPLATE += ' -interaction="batchmode" -f -{compiler} {infile}'

# LATEX_COMMAND_TEMPLATE='latexmk -cd -jobname=output -auxdir=/mnt -outdir=/mnt -synctex=1 -interaction="batchmode" -f -{compiler} {infile}'

class TestFilepath(unittest.TestCase):
    def test_check_length(self):
        self.assertRaises(PermissionError, check_filepath,
                          "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquy!")

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
            raise PermissionError(
                "Error: We only support directories with letters, numbers, underscores, hyphens and spaces in the filename before the .tex")
    if not re.match(INFILE_REGEX, path[-1]):
        raise PermissionError(
            "Error: We only support input files with letters, numbers, underscores, hyphens and spaces in the filename before the .tex")


app = Flask(__name__)


@app.route("/")
def main():
    return "Nothing to see here."


@app.route("/compile")
def callback():
    latexmk_args = {
        "compiler": request.args.get('compiler'),
        "infile": request.args.get('infile'),
        "auxdir": request.args.get('auxdir'),
        "outdir": request.args.get('outdir'),
    }
    latexmk_args["infile"] = latexmk_args["infile"].removeprefix(
        latexmk_args["auxdir"] + "/")

    try:
        check_filepath(latexmk_args["infile"])
    except PermissionError as e:
        return f"{e}"

    latexmk_args["infile"] = '"%s"' % latexmk_args["infile"]

    latexmk = LATEX_COMMAND_TEMPLATE.format_map(latexmk_args)

    args = {
        "uid": UID,
        "gid": GID,
        "image": TEXLIVE_IMAGE,
        "auxdir": latexmk_args["auxdir"],
        "command": latexmk,
        "timeout": TIMEOUT,
    }
    command = CMD_TEMPLATE.format_map(args)

    try:
        os.chdir(latexmk_args["auxdir"])
        code, output = subprocess.getstatusoutput(command)
        return output
    except subprocess.CalledProcessError as e:
        return ""


if __name__ == "__main__":
    unittest.main()
    app.run(host='0.0.0.0', port=6666, debug=True)

