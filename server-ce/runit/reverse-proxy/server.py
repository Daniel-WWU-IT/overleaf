from flask import Flask, request, Response
from bs4 import BeautifulSoup

import os, re, requests, sys

app = Flask(__name__)


# Helpers
def _injectScript(soup, file):
    bodyElement = soup.find('body')
    if bodyElement:
        scriptTag = soup.new_tag('script', src=file, type='text/javascript')
        bodyElement.append(scriptTag)


def _injectStylesheet(soup, file):
    bodyElement = soup.find('body')
    if bodyElement:
        styleTag = soup.new_tag('link', href=file, rel='stylesheet')
        bodyElement.append(styleTag)


def _appendStyle(tag, style):
    if tag == None:
        return

    styleNew = style
    if 'style' in tag and tag['style'] != '':
        styleNew = tag['style'] + '; ' + style
    tag['style'] = styleNew


def _buildMenu(soup, title, items, is_subdued=False):
    linkTag = soup.new_tag('a', attrs={'class': 'dropdown-toggle', 'data-toggle': 'dropdown', 'href': '#', 'aria-haspopup': 'true', 'aria-expanded': 'false', 'role': 'button'})
    linkTag.append(title)
    linkTag.append(soup.new_tag('b', attrs={'class': 'caret'}))

    menuTag = soup.new_tag('ul', attrs={'class': 'dropdown-menu'})
    for item in items:
        linkElem = soup.new_tag('a', id=item['id'], href=item['href'], target=item['target'])
        linkElem.append(item['title'])
        listElem = soup.new_tag('li')
        listElem.append(linkElem)
        menuTag.append(listElem)

    liTag = soup.new_tag('li')
    liTag['class'] = 'subdued dropdown' if is_subdued else 'dropdown'
    liTag.append(linkTag)
    liTag.append(menuTag)
    return liTag


# Content modifiers
def _modifyProjectPage(soup):
    # Inject the reverse proxy client-side script
    _injectScript(soup, '/js/reverse-proxy-proj.js')

    # Inject the MsgPopup files
    _injectScript(soup, '/js/jquery-msgpopup.js')
    _injectStylesheet(soup, '/stylesheets/jquery-msgpopup.css')

    # Add a 'Support' drop-down button
    ulElement = soup.find('ul', class_='navbar-right')
    if ulElement:
        os.getenv('SERVICE_DEBUG_MODE')
        menuEntries = [
              {'id': 'support-info', 'title': 'General information', 'href': '', 'target': '_blank'},
              {'id': 'support-docs', 'title': 'Documentation', 'href': 'https://www.overleaf.com/learn', 'target': '_blank'},
              {'id': 'support-contact', 'title': 'Contact us', 'href': 'https://hochschulcloud.nrw/de/kontakt', 'target': '_blank'}
        ]
        if os.getenv('SERVICE_DEBUG_MODE', 'false').casefold() == 'true'.casefold():
            menuEntries.append({'id': 'support-login', 'title': 'Relogin', 'href': '/login', 'target': '_self'})

        menu = _buildMenu(soup, 'Support', menuEntries, is_subdued=True)
        ulElement.insert(0, menu)

    # Hide unnecessary items of the 'Account' drop-down
    liElement = soup.find('li', class_='dropdown')
    if liElement:
        ulElement = liElement.find('ul', class_='dropdown-menu')
        if ulElement:
            for li in ulElement('li'):
                if not li.find('div'):
                    _appendStyle(li, 'display: none;')


def _modifyDocumentPage(soup):
    # Inject the reverse proxy client-side script
    _injectScript(soup, '/js/reverse-proxy-doc.js')


def _modifyLoginPage(soup):
    # Inject the reverse proxy client-side script
    _injectScript(soup, '/js/reverse-proxy-login.js')

    # Hide the login page elements
    cardElement = soup.find('div', class_='card')
    if cardElement:
        _appendStyle(cardElement, 'display: none;')
        parent = cardElement.find_parent()

        # Add a new info panel
        h1Element = soup.new_tag('h1', style='text-align: center;')
        h1Element.string = 'Automatic re-login'
        textElement = soup.new_tag('p', style='text-align: center;')
        textElement.string = 'Due to technical reasons, you need to be logged in again. This will just take a moment...'
        headerElement = soup.new_tag('div', class_='page-header')
        headerElement.append(h1Element)
        headerElement.append(textElement)
        cardElement = soup.new_tag('div', class_='card')
        cardElement.append(headerElement)
        parent.append(cardElement)

    ulElement = soup.find('ul', class_='navbar-right')
    if ulElement:
        _appendStyle(ulElement, 'display: none;')


def _modifyGenericPage(soup):
    # Inject version information
    _injectScript(soup, '/js/_version.js')

    # Inject jQuery
    _injectScript(soup, '/js/jquery.js')

    # Inject the reverse proxy stylesheet
    _injectStylesheet(soup, '/stylesheets/reverse-proxy.css')

    # Fix the footer widths
    divElement = soup.find('div', class_='site-footer-content')
    if divElement:
        ul = divElement.find('ul', class_='col-md-9')
        if ul:
            _appendStyle(ul, 'width: 50%;')
        ul = divElement.find('ul', class_='col-md-3')
        if ul:
            _appendStyle(ul, 'width: 50%;')

    # Fix the left footer
    linkElement = soup.find('a', href='https://www.overleaf.com/for/enterprises')
    if linkElement:
        linkElement['href'] = 'https://www.overleaf.com'
        linkElement['target'] = '_blank'


# Parse and modify the response based on the current path
def _parseResponse(resp, path):
    modifiers = {
        '/': _modifyProjectPage,
        '/project': _modifyProjectPage,
        '/project/[0-9A-Fa-f]{24}': _modifyDocumentPage,
        '/login': _modifyLoginPage,
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
                            url=f'http://localhost:3000{request.full_path}',
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
