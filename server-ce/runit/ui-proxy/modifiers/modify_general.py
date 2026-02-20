from bs4 import BeautifulSoup

from .utils import inject_script


def modify_general(soup: BeautifulSoup) -> None:
  inject_script(soup, '/js/ui-proxy/jquery.js')

  inject_script(soup, '/js/ui-proxy/mutations.js')
  inject_script(soup, '/js/ui-proxy/modify-general.js')
