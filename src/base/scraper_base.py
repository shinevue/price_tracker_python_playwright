from abc import ABC, abstractmethod

import lxml.etree
import lxml.html
import unicodedata
from urllib.parse import unquote

from src.base.product_base import Product
from src.logger import Log


log = Log()


class PageContent:
    """
    Responsible for processing page's raw data to a parser-friendly form.
    """
    def __init__(
        self, url: str, status_code: int, headers: dict, body: bytes, raw_html: str
    ):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.raw_html = raw_html

    @property
    def encoding(self) -> str | None:
        content_type = self.headers["content-type"].split(";")
        try:
            encoding = content_type[1].strip().split("=")[1].strip()
            return "latin1" if encoding == "latin-1" else encoding
        except IndexError:
            return None

    @property
    def html_tree(self) -> lxml.etree.ElementTree:
        tree_parser = lxml.html.HTMLParser(remove_comments=True, recover=True)
        normalized_html = unicodedata.normalize("NFKC", unquote(self.raw_html.strip()))
        return lxml.html.fromstring(normalized_html, parser=tree_parser)


class Scraper(ABC):
    def __init__(self, page_content: PageContent) -> None:
        self.page = page_content


class CategoryScraper(Scraper):
    @abstractmethod
    def extract_products_urls(self) -> list[str | None]:
        pass

    @abstractmethod
    def extract_products_data(self) -> list[Product | None]:
        pass

class ProductScraper(Scraper):
    @abstractmethod
    def extract_product_data(self) -> Product:
        pass

