from flask import Flask, request, Response
from bs4 import BeautifulSoup

import requests, sys

app = Flask(__name__)


# Helpers
def _appendStyle(tag, style):
    if tag == None:
        pass
    
    styleNew = style
    if 'style' in tag and tag['style'] != '':
        styleNew = tag['style'] + '; ' + style
    tag['style'] = styleNew


# Content modifiers
def _modifyProjectPage(soup):
    # Hide the 'Account' button
    liElement = soup.find('li', class_='dropdown', dropdown=True)
    if liElement and liElement.find('a', class_='dropdown-toggle', attrs={"dropdown-toggle": True}):
        _appendStyle(liElement, 'display: none;')


# Parse and modify the response based on the current path
def _parseResponse(resp, path):
    modifiers = {
        '/': _modifyProjectPage,
        '/project': _modifyProjectPage
    }

    content = resp.content
    if path in modifiers:
        try:
            soup = BeautifulSoup(resp.text, 'lxml')
            modifiers[path](soup)
            content = str(soup)
        except Exception as e:
            app.logger.error(f'Handling the content of {path} threw an exception: {e} ({type(e)})')
    return content


# Route all paths through the proxy
@app.route('/', defaults={'path': '/'})
@app.route('/<path:path>')
def proxy(path):
    resp = requests.request(method=request.method,
                            url=f'http://127.0.0.1:3000{request.full_path}',
                            headers={key: value for (key, value) in request.headers if key != 'Host'},
                            data=request.form.to_dict(),
                            cookies=request.cookies)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

    content = _parseResponse(resp, request.path)
    response = Response(content, resp.status_code, headers)

    cookies = resp.cookies.get_dict('localhost.local')
    for key in cookies:
        response.set_cookie(key, cookies[key], samesite='None', secure=True)

    return response
