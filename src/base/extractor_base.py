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
    Product of Browser instances' scrapes, prepared for extraction.
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



class SitemapContent(PageContent):
    def __init__(self, url: str, status_code: int, headers: dict, body: bytes, raw_html: str):
        super().__init__(url, status_code, headers, body, raw_html)

    @property
    def xml_tree(self) -> lxml.etree.ElementTree:
        parser = lxml.etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        xml_tree = lxml.etree.fromstring(self.raw_html.encode('utf-8'), parser=parser)
        return xml_tree


class Extractor(ABC):
    def __init__(self, page_content: PageContent) -> None:
        self.page = page_content


class CategoryExtractor(Extractor):
    @abstractmethod
    def extract_max_pagination(self) -> int:
        pass

    @abstractmethod
    def extract_category_page(self) -> list[Product | None]:
        pass

class ProductExtractor(Extractor):
    @abstractmethod
    def extract_product_data(self) -> Product:
        pass


class SitemapExtractor(Extractor):
    def __init__(self, sitemap_content: SitemapContent):
        self.sitemap_content = sitemap_content

    def extract_categories(self) -> list[str]:
        ns = {'s': "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = self.sitemap_content.xml_tree.xpath('//s:url/s:loc', namespaces=ns)
        sitemap_urls = []
        for url in urls:
            sitemap_urls.append(url.text)
        return sorted(sitemap_urls)
