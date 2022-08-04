import subprocess, re, requests, os, fnmatch
from flask import *
from urllib.parse import urlparse, parse_qs
from html import escape


app = Flask(__name__)
client = requests.session()


def _error(msg, code=500):
    app.logger.error(msg)
    abort(code)


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
        _error('Email address missing', 400)
    password = request.args.get('password', '')

    result = subprocess.run(['grunt', 'user:create', '--email=' + email], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        _error('Creating the user account failed (process error)')

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
    except BaseException as e:
        _error('Creating a user resulted in an exception: ' + str(e))


def login():
    email = request.args.get('email', '')
    password = request.args.get('password', '')
    if email == '' or password == '':
        _error('Login: Email or password missing', 400)

    try:
        response = make_response(redirect('/project', code=302))

        login = perform_login(email, password)

        # Copy all Sharelatex-specific headers and cookies
        for key in login.headers:
            if 'sharelatex' in key.casefold():
                response.headers[key] = login.headers[key]

        cookies = login.cookies.get_dict('localhost.local')
        for key in cookies:
            if 'sharelatex' in key.casefold():
                response.set_cookie(key, cookies[key])

        return response
    except BaseException as e:
        _error('Logging in a user resulted in an exception: ' + str(e))


@app.before_request
def verify_client():
    # Allowed remote addresses are passed via the env variable REMOTE_API_ALLOWED_CLIENTS; wildcards are supported
    allowed_clients = os.getenv('REMOTE_API_ALLOWED_CLIENTS', '')

    # Only let requests from allowed remote addresses through
    for allowed_client in [s.strip() for s in allowed_clients.split(',')]:
        if fnmatch.fnmatchcase(request.remote_addr.casefold(), allowed_client.casefold()):
            break
    else:
        _error(f'Request from {request.remote_addr} is not allowed', 503)


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
        _error('Unknown action', 404)
