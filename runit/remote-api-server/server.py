import subprocess, re, requests, os, fnmatch, base64
from flask import *
from cryptography.fernet import Fernet
from urllib.parse import urlparse, parse_qs
from html import escape


app = Flask(__name__)
client = requests.session()


# Cryptography functions
def _encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())


def _decrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.decrypt(data.encode()).decode()


# Response helpers
def _data_response(data={}, data_key=''):
    json_data = json.dumps(data)
    resp = app.response_class(
        response=_encrypt_data(json_data, data_key) if data_key != '' else json_data,
        status=200,
        mimetype='application/json'
    )
    return resp


def _error(msg, code=500):
    app.logger.error(msg)
    abort(code)


# Main functions
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
            return _data_response()
        else:
          return _data_response({'url': link})
    except BaseException as e:
        _error('Creating a user resulted in an exception: ' + str(e))


def login(data_enc_key):
    email = request.args.get('email', '')
    password = request.args.get('password', '')
    if email == '' or password == '':
        _error('Login: Email or password missing', 400)

    try:
        login = perform_login(email, password)

        # Get all Sharelatex-specific headers and cookies
        data = {'headers': {}, 'cookies': {}}
        for key in login.headers:
            if 'sharelatex' in key.casefold():
                data['headers'][key] = login.headers[key]

        cookies = login.cookies.get_dict('localhost.local')
        for key in cookies:
            if 'sharelatex' in key.casefold():
                data['cookies'][key] = cookies[key]

        return _data_response(data, data_enc_key)
    except BaseException as e:
        _error('Logging in a user resulted in an exception: ' + str(e))


def open_projects(data_enc_key):
    data = request.args.get('data', '')
    if data == '':
        _error('Open: Data missing', 400)
    data = _decrypt_data(data, data_enc_key)

    try:
        req_data = json.loads(data)
        response = make_response(redirect(os.getenv('SHARELATEX_SITE_URL', '').rstrip('/') + '/project', code=302))

        # Copy all specified headers and cookies into the request
        for key in req_data['headers']:
            response.headers[key] = req_data['headers'][key]

        for key in req_data['cookies']:
            response.set_cookie(key, req_data['cookies'][key])

        return response
    except BaseException as e:
        _error('Opening the projects resulted in an exception: ' + str(e))


# API key handling
def verify_api_key():
    api_key = os.getenv('REMOTE_API_KEY', '')
    if api_key == '':
        _error('No API key set', 500)

    req_key = request.args.get('apikey', '')
    if req_key != api_key:
        _error('Invalid API key specified', 503)


# App routing
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
    # Get the key used to encrypt login data; specifying this is mandatory
    data_enc_key = os.getenv('REMOTE_API_DATA_KEY', '')
    if data_enc_key == '':
        _error('No data key set', 500)
    data_enc_key = base64.b64encode(data_enc_key.encode()) # Required by Fernet

    action = request.args.get('action', 'create-and-login')
    if action.casefold() == 'create':
        verify_api_key()
        return create_user()
    elif action.casefold() == 'login':
        verify_api_key()
        return login(data_enc_key)
    elif action.casefold() == 'create-and-login':
        verify_api_key()
        create_user()
        return login(data_enc_key)
    elif action.casefold() == 'open-projects':
        # This EP is public
        return open_projects(data_enc_key)
    else:
        _error('Unknown action', 404)
