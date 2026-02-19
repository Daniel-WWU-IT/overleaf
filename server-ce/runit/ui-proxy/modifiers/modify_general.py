from bs4 import BeautifulSoup

from .utils import inject_script


def modify_general(soup: BeautifulSoup) -> None:
  # 3rd party libraries
  inject_script(soup, '/js/ui-proxy/jquery.js')

  # Internal helpers
  inject_script(soup, '/js/ui-proxy/mutations.js')
