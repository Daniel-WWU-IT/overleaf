import base64
import fnmatch
import os
import re
import subprocess
from urllib.parse import urlparse, parse_qs

import flask
import requests
from cryptography.fernet import Fernet

app = flask.Flask(__name__)


# Cryptography functions
def _encrypt_data(data, key):
  fernet = Fernet(key)
  return fernet.encrypt(data.encode())


def _decrypt_data(data, key):
  fernet = Fernet(key)
  return fernet.decrypt(data.encode()).decode()


# Response helpers
def _data_response(data=None, data_key=''):
  json_data = flask.json.dumps(data if data is not None else {})
  resp = app.response_class(
    response=_encrypt_data(json_data, data_key) if data_key != '' else json_data,
    status=200,
    mimetype='application/json'
  )
  return resp


def _error(client, msg, code=500):
  app.logger.error(msg)
  if client is not None:
    client.close()
  flask.abort(code)


def _resolve_url(path, *, use_origin=False):
  host_url = os.getenv('SHARELATEX_SITE_URL', '')
  if use_origin:
    try:
      host_url = flask.request.args.get('origin', '')
      if host_url == '':
        host_url = flask.request.headers['X-Overleaf-Origin']
    except:
      pass

  return host_url.rstrip('/') + '/' + path.lstrip('/')


def _get_header_password():
  if 'X-Overleaf-Password' in flask.request.headers:
    return flask.request.headers['X-Overleaf-Password']
  return ''


# Main functions
def extract_auth_tokens(client, link):
  response = client.get(link)

  regex = r"<input\s*name=[\"']_csrf[\"']\s*type=[\"']hidden[\"']\s*value=[\"']([a-zA-z0-9-]*)[\"'].*>"
  matches = re.finditer(regex, response.text, re.MULTILINE | re.DOTALL)
  return next(matches).group(1).strip(), response.headers, response.cookies


def set_password(client, link, password):
  # Get auth tokens from activation page
  csrf, h, c = extract_auth_tokens(client, link)

  # Perform POST request to set the password
  params = parse_qs(urlparse(link).query)
  return client.post(_resolve_url('/user/password/set'),
                     data={'_csrf': csrf, 'passwordResetToken': params['token'][0], 'password': password})


def perform_login(client, email, password):
  # Get auth tokens from login page
  csrf, h, c = extract_auth_tokens(client, _resolve_url('/login'))

  # Perform POST request to log the user in
  return client.post(_resolve_url('/login'), data={'_csrf': csrf, 'email': email, 'password': password})


def create_user(client):
  email = flask.request.args.get('email', '')
  if email == '':
    _error(client, 'Email address missing', 400)
  password = _get_header_password()

  result = subprocess.run(['grunt', 'user:create', '--email=' + email], universal_newlines=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  if result.returncode != 0:
    _error(client, 'Creating the user account failed (process error)')

  try:
    output = str(result.stdout)
    regex = r".*Successfully created .* as a user.*(^\s*http.*\s*$).*Done"
    matches = re.finditer(regex, output, re.MULTILINE | re.DOTALL)
    link = next(matches).group(1).strip()

    if password != '':
      set_password(client, link, password)
      return _data_response()
    else:
      return _data_response({'url': link})
  except BaseException as e:
    _error(client, 'Creating a user resulted in an exception: ' + str(e))


def login(client, data_enc_key):
  email = flask.request.args.get('email', '')
  password = _get_header_password()
  if email == '' or password == '':
    _error(client, 'Login: Email or password missing', 400)

  try:
    resp = perform_login(client, email, password)

    # Get all Sharelatex-specific headers and cookies
    data = {'headers': {}, 'cookies': {}}
    for key in resp.headers:
      if 'sharelatex' in key.casefold():
        data['headers'][key] = resp.headers[key]

    cookies_loc = os.getenv('COOKIES_LOCATION', urlparse(_resolve_url('')).netloc)
    cookies = resp.cookies.get_dict(cookies_loc)
    for key in cookies:
      if 'sharelatex' in key.casefold():
        data['cookies'][key] = cookies[key]

    return _data_response(data, data_enc_key)
  except BaseException as e:
    _error(client, 'Logging in a user resulted in an exception: ' + str(e))


def open_projects(client, data_enc_key):
  data = flask.request.args.get('data', '')
  if data == '':
    _error(client, 'Open: Data missing', 400)
  data = _decrypt_data(data, data_enc_key)

  try:
    req_data = flask.json.loads(data)
    response = flask.make_response(flask.redirect(_resolve_url('/project', use_origin=True), code=302))

    # Copy all specified headers and cookies into the request
    for key in req_data['headers']:
      response.headers[key] = req_data['headers'][key]

    for key in req_data['cookies']:
      response.set_cookie(key, req_data['cookies'][key], samesite='None', secure=True)

    return response
  except BaseException as e:
    _error(client, 'Opening the projects resulted in an exception: ' + str(e))


def delete_user(client):
  email = flask.request.args.get('email', '')
  if email == '':
    _error(client, 'Email address missing', 400)

  result = subprocess.run(['grunt', 'user:delete', '--email=' + email])
  if result.returncode != 0:
    _error(client, 'Deleting the user account failed (process error)')

  # We just assume that deleting the user worked
  return _data_response()


# API key handling
def verify_api_key(client):
  api_key = os.getenv('REMOTE_API_KEY', '')
  if api_key == '':
    _error(client, 'No API key set', 500)

  if 'X-Overleaf-Apikey' in flask.request.headers:
    req_key = flask.request.headers['X-Overleaf-Apikey']
    if req_key != api_key:
      _error(client, 'Invalid API key specified', 503)
  else:
    _error(client, 'No API key provided', 503)


# App routing
@app.before_request
def verify_client():
  # Allowed remote addresses are passed via the env variable REMOTE_API_ALLOWED_CLIENTS; wildcards are supported
  allowed_clients = os.getenv('REMOTE_API_ALLOWED_CLIENTS', '')

  # Only let requests from allowed remote addresses through
  for allowed_client in [s.strip() for s in allowed_clients.split(',')]:
    if fnmatch.fnmatchcase(flask.request.remote_addr.casefold(), allowed_client.casefold()):
      break
  else:
    _error(None, f'Request from {flask.request.remote_addr} is not allowed', 503)


@app.route("/")
def regsvc():
  # Requests session
  client = requests.Session()

  # Get all extended headers
  for header in flask.request.headers:
    if header[0].startswith('X-Forwarded'):
      client.headers[header[0]] = header[1]

  # Get the key used to encrypt login data; specifying this is mandatory
  data_enc_key = os.getenv('REMOTE_API_DATA_KEY', '')
  if data_enc_key == '':
    _error(client, 'No data key set', 500)
  data_enc_key = base64.b64encode(data_enc_key.encode())  # Required by Fernet

  action = flask.request.args.get('action', 'create-and-login')
  result = None
  if action.casefold() == 'create':
    verify_api_key(client)
    result = create_user(client)
  elif action.casefold() == 'login':
    verify_api_key(client)
    result = login(client, data_enc_key)
  elif action.casefold() == 'create-and-login':
    verify_api_key(client)
    create_user(client)
    result = login(client, data_enc_key)
  elif action.casefold() == 'open-projects':
    # This EP is public
    result = open_projects(client, data_enc_key)
  elif action.casefold() == 'delete':
    verify_api_key(client)
    result = delete_user(client)
  elif action.casefold() == 'echo':
    result = "ECHO"
  else:
    _error(client, 'Unknown action', 404)

  client.close()
  return result
