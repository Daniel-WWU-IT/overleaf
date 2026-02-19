from bs4 import BeautifulSoup


def inject_script(soup: BeautifulSoup, file: str) -> None:
  if (body_elem := soup.find("body")) is not None:
    script_tag = soup.new_tag("script", src=file, type="text/javascript")
    body_elem.append(script_tag)
