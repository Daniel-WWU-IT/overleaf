from flask import Flask, request, Response
from bs4 import BeautifulSoup

import re, requests, sys

app = Flask(__name__)


# Helpers
def _appendStyle(tag, style):
    if tag == None:
        pass
    
    styleNew = style
    if 'style' in tag and tag['style'] != '':
        styleNew = tag['style'] + '; ' + style
    tag['style'] = styleNew
    
    
def _buildMenu(soup, title, items, is_subdued=False):
    linkTag = soup.new_tag('a', attrs={'class': 'dropdown-toggle', 'dropdown-toggle': True, 'href': '', 'aria-haspopup': 'true', 'aria-expanded': 'false'})
    linkTag.append(title)
    linkTag.append(soup.new_tag('b', attrs={'class': 'caret'}))

    menuTag = soup.new_tag('ul', attrs={'class': 'dropdown-menu'})
    for item in items:
        linkElem = soup.new_tag('a', href=item['href'], target=item['target'])
        linkElem.append(item['title'])
        listElem = soup.new_tag('li')
        listElem.append(linkElem)
        menuTag.append(listElem)
        
    liTag = soup.new_tag('li', dropdown=True)
    liTag['class'] = 'subdued dropdown' if is_subdued else 'dropdown'
    liTag.append(linkTag)
    liTag.append(menuTag)
    return liTag


# Content modifiers
def _modifyProjectPage(soup):
    # Add a 'Support' drop-down button
    ulElement = soup.find('ul', class_='navbar-right')
    if ulElement:
        menu = _buildMenu(soup, 'Support', [
            {'title': 'Documentation', 'href': 'https://www.overleaf.com/learn', 'target': '_blank'}
        ], is_subdued=True)
        ulElement.insert(0, menu)
    
    # Hide unnecessary items of the 'Account' drop-down
    liElement = soup.find('li', class_='dropdown', dropdown=True)
    if liElement:
        ulElement = liElement.find('ul', class_='dropdown-menu')
        if ulElement:
            for li in ulElement('li'):
                if not li.find('div'):
                    _appendStyle(li, 'display: none;')


def _modifyDocumentPage(soup):
    # Inject the reverse proxy client-side script
    bodyElement = soup.find('body')
    if bodyElement:
        scriptTag = soup.new_tag('script', src='/js/reverse-proxy-doc.js', type='text/javascript')
        bodyElement.append(scriptTag)
        
        
def _modifyGenericPage(soup):
    # Inject the reverse proxy stylesheet
    bodyElement = soup.find('body')
    if bodyElement:
        styleTag = soup.new_tag('link', href='/stylesheets/reverse-proxy.css', rel='stylesheet')
        bodyElement.append(styleTag)


# Parse and modify the response based on the current path
def _parseResponse(resp, path):
    modifiers = {
        '/': _modifyProjectPage,
        '/project': _modifyProjectPage,
        '/project/[0-9A-Fa-f]{24}': _modifyDocumentPage
    }

    content = resp.content
    
    for mod in modifiers:
        if re.match('^' + mod + '$', path):
            try:
                soup = BeautifulSoup(resp.text, 'lxml')
                _modifyGenericPage(soup)
                modifiers[mod](soup)
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
