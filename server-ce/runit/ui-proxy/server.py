import os
import re

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, Response

from modifiers import modify_general, modify_project

app = Flask(__name__)

# Do not include these headers in the proxied response
excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]

# Page modifiers
modifiers = {
  "/": modify_project,
  "/project": modify_project,
  "/project/[0-9A-Fa-f]{24}": None,
  "/login": None,
}


# Process and modify the response based on the current path
def _process_content(resp: Response, path: str) -> str:
  content = resp.content

  for mod in modifiers:
    if re.match("^" + mod + "$", path):
      try:
        soup = BeautifulSoup(resp.text, "lxml")
        modify_general(soup)
        if callable(modifiers[mod]):
          modifiers[mod](soup)
        content = str(soup)

      except Exception as e:
        app.logger.error(f"Handling the content of {path} threw an exception: {e} ({type(e)})")

  return content

# Route all paths through the proxy
@app.route("/", defaults={"path": "/"})
@app.route("/<path:path>")
def proxy(path: str) -> Response:
  req_resp = requests.request(method=request.method,
                              url=f"http://localhost:4000{request.full_path}",
                              headers={key: value for (key, value) in request.headers if key != "Host"},
                              data=request.form.to_dict(),
                              cookies=request.cookies)

  resp = Response(
    _process_content(req_resp, request.path) if os.getenv("DISABLE_UI_PROXY", "") != "true" else req_resp.content,
    status=req_resp.status_code,
    headers={name: value for (name, value) in req_resp.raw.headers.items() if name.lower() not in excluded_headers}
  )

  cookies = req_resp.cookies.get_dict("localhost.local")
  for key in cookies:
    resp.set_cookie(key, cookies[key], samesite="None", secure=True)

  return resp
