from bs4 import BeautifulSoup

from .utils import inject_script


def modify_project(soup: BeautifulSoup) -> None:
  inject_script(soup, '/js/ui-proxy/modify-project.js')
