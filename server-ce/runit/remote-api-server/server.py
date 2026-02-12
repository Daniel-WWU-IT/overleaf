import fnmatch
import os
import random
import re
import string
import subprocess
from urllib.parse import urlparse, parse_qs

import flask
import requests

app = flask.Flask(__name__)


# Debugging
def _debug_print(msg, *, top_line = False, bottom_line = False):
  if os.getenv('DEBUG_INFORMATION').casefold() == 'true':
    if top_line:
      print('\033[95m\033[1m----------------------------------------', flush=True)
    print(f'\033[93m\033[1m{msg}', flush=True)
    if bottom_line:
      print('\033[95m\033[1m----------------------------------------', flush=True)


# Response helpers
def _data_response(data=None, headers=None):
  json_data = flask.json.dumps(data if data is not None else {})
  resp = app.response_class(
    response=json_data,
    status=200,
    mimetype='application/json'
  )
  if headers is not None:
    resp.headers = headers
  return resp


def _error(client, msg, code=500):
  _debug_print(f'Aborting due to error: {msg} (code={code})', bottom_line=True)

  app.logger.error(msg)
  if client is not None:
    client.close()
  flask.abort(code)


def _resolve_url(path):
  host_url = os.getenv('OVERLEAF_SITE_URL', '')
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
  csrf = next(matches).group(1).strip()

  _debug_print(f'\tAuth tokens: {csrf}; cookies={str(response.cookies)}, headers={str(response.headers)}')

  return csrf, response.headers, response.cookies


def set_password(client, link, email, password):
  # Get auth tokens from activation page
  csrf, h, c = extract_auth_tokens(client, link)

  _debug_print(f'Setting password for: {email}, password: {password}')

  # Perform POST request to set the password
  params = parse_qs(urlparse(link).query)
  resp = client.post(_resolve_url('/user/password/set'),
                     data={'_csrf': csrf, 'passwordResetToken': params['token'][0], 'email': email, 'password': password},
                     cookies=c.get_dict()
                     )
  _debug_print(f'\t{str(resp)}')

  return resp


def create_user(client):
  email = flask.request.args.get('email', '')
  if email == '':
    _error(client, 'Email address missing', 400)
  password = ''.join(random.choices(string.ascii_letters + string.digits, k=32))  # We just generate a random password

  _debug_print(f'Creating user: {email}, password: {password}')

  result = subprocess.run(['grunt', 'user:create', '--email=' + email], universal_newlines=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  if result.returncode == 0:
    _debug_print(f'User created')
  else:
    _error(client, 'Creating the user account failed (process error)')

  try:
    output = str(result.stdout)
    regex = r".*Successfully created .* as a user.*(^\s*http.*\s*$).*Done"
    matches = re.finditer(regex, output, re.MULTILINE | re.DOTALL)
    link = next(matches).group(1).strip()

    if password != '':
      resp = set_password(client, link, email, password)
      if resp.status_code >= 400:
        _error(client, 'Unable to set password: ' + resp.content, resp.status_code)
      return _data_response({'email': email, 'password': password})
    else:
      return _data_response({'url': link})
  except BaseException as e:
    _error(client, 'Creating a user resulted in an exception: ' + str(e))


def delete_user(client):
  email = flask.request.args.get('email', '')
  if email == '':
    _error(client, 'Email address missing', 400)

  _debug_print(f'Deleting user: {email}')

  result = subprocess.run(['grunt', 'user:delete', '--email=' + email])
  if result.returncode == 0:
    _debug_print('User deleted')
  else:
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

  action = flask.request.args.get('action', 'echo')
  _debug_print(f'Executing action: {action}', top_line=True)

  result = None
  if action.casefold() == 'create':
    verify_api_key(client)
    result = create_user(client)
  elif action.casefold() == 'delete':
    verify_api_key(client)
    result = delete_user(client)
  elif action.casefold() == 'echo':
    result = "ECHO"
  else:
    _error(client, 'Unknown action', 404)

  _debug_print(f'Execution ({action}) finished: {str(result)}', bottom_line=True)

  client.close()
  return result
