#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from http import HTTPStatus

from flask import Flask, request, Response


# Various settings can be overridden via environment variables
TEXLIVE_IMAGE = os.environ.get("TEXLIVE_IMAGE","docker.io/texlive/texlive:TL2024-historic")
UID = os.environ.get("COMPILER_HOST_UID", "33")
GID = os.environ.get("COMPILER_HOST_GID", "33")
TIMEOUT = os.environ.get("TIMEOUT", 600)


def _log_error(exc: Exception) -> None:
    with open("/tmp/host.error.log", "a") as outfile:
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


# Flask and its endpoints
app = Flask(__name__)


@app.route("/")
def i_am_alive() -> Response:
    return Response("Nothing to see here (but I am alive).")


@app.route("/compile")
def start_compile() -> Response:
    # Placeholder strings for launching the compiler
    cmd_template = "timeout {timeout} podman run"
    cmd_template += " -u{uid}:{gid} -v {auxdir}:{auxdir} -w {auxdir}"
    cmd_template += " --rm --network=none {image} {command}"
    latex_command_template = "latexmk -cd -jobname=output"
    latex_command_template += " -auxdir={auxdir} -outdir={outdir} -synctex=1"
    latex_command_template += " -interaction=batchmode -f -{compiler} {infile}"

    latexmk_args = {
        "compiler": request.args.get("compiler"),
        "infile": request.args.get("infile"),
        "auxdir": request.args.get("auxdir"),
        "outdir": request.args.get("outdir"),
    }
    latexmk_args["infile"] = latexmk_args["infile"].removeprefix(latexmk_args["auxdir"] + "/")
    try:
        _check_filepath(latexmk_args["infile"])
    except PermissionError as e:
        return Response(str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    latexmk_args["infile"] = f"\"{latexmk_args['infile']}\""
    latexmk = latex_command_template.format_map(latexmk_args)

    args = {
        "uid": UID,
        "gid": GID,
        "image": TEXLIVE_IMAGE,
        "auxdir": latexmk_args["auxdir"],
        "command": latexmk,
        "timeout": TIMEOUT,
    }
    command = cmd_template.format_map(args)
    try:
        os.chdir(latexmk_args["auxdir"])
        code, output = subprocess.getstatusoutput(command)
        if code != 0:
            _log_error(Exception(f"LaTeXMK: [{code}] {output}"))
        return Response(output, status=HTTPStatus.OK if code == 0 else HTTPStatus.INTERNAL_SERVER_ERROR)
    except subprocess.CalledProcessError as e:
        return Response(str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6666, debug=True)
