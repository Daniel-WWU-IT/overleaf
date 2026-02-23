from bs4 import BeautifulSoup

from .utils import inject_script, inject_stylesheet


def modify_general(soup: BeautifulSoup) -> None:
  inject_script(soup, '/js/ui-proxy/jquery.js')
  inject_script(soup, '/js/ui-proxy/jquery-msgpopup.js')

  inject_script(soup, '/js/ui-proxy/_version.js')
  inject_script(soup, '/js/ui-proxy/mutations.js')
  inject_script(soup, '/js/ui-proxy/modify-general.js')

  inject_stylesheet(soup, "/stylesheets/ui-proxy/jquery-msgpopup.css")
