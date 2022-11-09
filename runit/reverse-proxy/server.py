from flask import Flask,request,redirect,Response
import requests, sys

app = Flask(__name__)

# Route all paths through the proxy
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    return redirect()

# Redirect to the actual web service
def redirect():
    resp = requests.request(method=request.method,
                            url=f'http://127.0.0.1:3000{request.full_path}',
                            headers={key: value for (key, value) in request.headers if key != 'Host'},
                            data=request.form.to_dict(),
                            cookies=request.cookies)
    
    content = resp.text
    # TODO: Parse & modify text, depending on the actual location/path

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    
    response = Response(content, resp.status_code, headers)

    cookies = resp.cookies.get_dict('localhost.local')
    for key in cookies:
        response.set_cookie(key, cookies[key], samesite='None', secure=True)

    return response
