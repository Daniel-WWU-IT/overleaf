import subprocess, re, requests
from flask import *
from urllib.parse import urlparse, parse_qs
from html import escape

app = Flask(__name__)

def set_password(link, password):
    url = urlparse(link)
    params = parse_qs(url.query)

    client = requests.session()

    # Get CSRF token from activation page
    redirectUrl = url._replace(netloc='localhost')._replace(scheme='http')
    response = client.get(redirectUrl.geturl())

    regex = r"<input\s*name=[\"']_csrf[\"']\s*type=[\"']hidden[\"']\s*value=[\"']([a-zA-z0-9-]*)[\"']>"
    matches = re.finditer(regex, response.text, re.MULTILINE|re.DOTALL)
    csrf = next(matches).group(1).strip()

    # Perform POST request to set the password
    client.post('http://localhost/user/password/set', data={'_csrf': csrf, 'passwordResetToken': params['token'][0], 'password': password})

@app.route("/")
def create_user():
    email = request.args.get('email', '')
    if email == '':
        abort(400)
    password = request.args.get('password', '')

    result = subprocess.run(['grunt', 'user:create', '--email=' + email], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        abort(500)

    try:
        output = str(result.stdout)
        regex = r".*Successfully created .* as a user.*(^\s*https.*\s*$).*Done"
        matches = re.finditer(regex, output, re.MULTILINE|re.DOTALL)
        link = next(matches).group(1).strip()

        if password != '':
            set_password(link, password)
            return redirect('/login', code=302)
        else:
            return '<a href="' + link + '">' + escape(link) + '</a>'
    except:
        abort(503)
