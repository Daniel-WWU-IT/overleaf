import subprocess, re, requests
from flask import *
from urllib.parse import urlparse, parse_qs
from html import escape


app = Flask(__name__)
client = requests.session()


def extract_auth_tokens(link):
    response = client.get(link)

    regex = r"<input\s*name=[\"']_csrf[\"']\s*type=[\"']hidden[\"']\s*value=[\"']([a-zA-z0-9-]*)[\"'].*>"
    matches = re.finditer(regex, response.text, re.MULTILINE|re.DOTALL)
    return next(matches).group(1).strip(), response.headers, response.cookies


def set_password(link, password):
    # Get auth tokens from activation page
    csrf, h, c = extract_auth_tokens(link)

    # Perform POST request to set the password
    params = parse_qs(urlparse(link).query)
    return client.post('http://localhost/user/password/set', data={'_csrf': csrf, 'passwordResetToken': params['token'][0], 'password': password})


def perform_login(email, password):
    # Get auth tokens from login page
    csrf, h, c = extract_auth_tokens('http://localhost/login')

    # Perform POST request to login the user
    return client.post('http://localhost/login', data={'_csrf': csrf, 'email': email, 'password': password})


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
            link = urlparse(link)._replace(netloc='localhost')._replace(scheme='http').geturl()
            set_password(link, password)
            return redirect('/login', code=302)
        else:
            return '<a href="' + link + '">' + escape(link) + '</a>'
    except:
        abort(503)


def login():
    email = request.args.get('email', '')
    password = request.args.get('password', '')
    if email == '' or password == '':
        abort(400)

    try:
        login = perform_login(email, password)

        response = make_response(redirect('/project', code=302))
        for key in login.headers:
            response.headers[key] = login.headers[key]
        cookies = login.cookies.get_dict('localhost.local')
        for key in cookies:
            response.set_cookie(key, cookies[key])

        return response
    except:
        abort(503)


@app.route("/")
def regsvc():
    action = request.args.get('action', 'create-and-login')

    if action.casefold() == 'create':
        return create_user()
    elif action.casefold() == 'login':
        return login()
    elif action.casefold() == 'create-and-login':
        create_user()
        return login()
    else:
        abort(404)
