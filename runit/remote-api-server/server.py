#!/usr/bin/python3
from flask import *
import subprocess, re

app = Flask(__name__)

@app.route("/")
def create_user():
    email = request.args.get('email', '')
    if email == '':
        abort(400)

    result = subprocess.run(['grunt', 'user:create', '--email=' + email], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        abort(500)

    try:
        output = str(result.stdout)
        regex = r".*Successfully created .* as a user.*(^\s*https.*\s*$).*Done"
        matches = re.finditer(regex, output, re.MULTILINE|re.DOTALL)
        link = next(matches).group(1).strip()
        return link
    except:
        abort(503)
