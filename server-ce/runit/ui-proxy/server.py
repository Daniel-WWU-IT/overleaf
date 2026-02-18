import requests
from flask import Flask, request, Response

app = Flask(__name__)

# Do not include these headers in the proxied response
excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]


# Route all paths through the proxy
@app.route("/", defaults={"path": "/"})
@app.route("/<path:path>")
def proxy(path):
  resp = requests.request(method=request.method,
                          url=f"http://localhost:4000{request.full_path}",
                          headers={key: value for (key, value) in request.headers if key != "Host"},
                          data=request.form.to_dict(),
                          cookies=request.cookies)

  response = Response(
    resp.content,
    status=resp.status_code,
    headers={name: value for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers}
  )

  cookies = resp.cookies.get_dict("localhost.local")
  for key in cookies:
    response.set_cookie(key, cookies[key], samesite="None", secure=True)

  return response
