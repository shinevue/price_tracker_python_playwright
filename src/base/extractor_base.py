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
        """Method responsible for extracting page's encoding from it's headers. """
        content_type = self.headers["content-type"].split(";")
        try:
            encoding = content_type[1].strip().split("=")[1].strip()
            return "latin1" if encoding == "latin-1" else encoding
        except IndexError:
            return None

    @property
    def html_tree(self) -> lxml.etree.ElementTree:
        """Method responsible for parsing raw_html to lxml tree."""
        tree_parser = lxml.html.HTMLParser(remove_comments=True, recover=True)
        normalized_html = unicodedata.normalize("NFKC", unquote(self.raw_html.strip()))
        return lxml.html.fromstring(normalized_html, parser=tree_parser)



class SitemapContent(PageContent):
    """
    PageContent variation, but representing the content of XML sitemap.
    """
    def __init__(self, url: str, status_code: int, headers: dict, body: bytes, raw_html: str):
        super().__init__(url, status_code, headers, body, raw_html)

    @property
    def xml_tree(self) -> lxml.etree.ElementTree:
        parser = lxml.etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        xml_tree = lxml.etree.fromstring(self.raw_html.encode('utf-8'), parser=parser)
        return xml_tree


class Extractor(ABC):
    """
    Abstract Base Class for all Extractors, responsible for extracting data from PageContent objects.
    """
    def __init__(self, page_content: PageContent) -> None:
        self.page = page_content


class CategoryExtractor(Extractor):
    """
    Abstract Base Class for extracting data from category pages.
    """
    @abstractmethod
    def extract_max_pagination(self) -> int:
        """Function responsible for extracting number of pages of pagination for given category page."""
        pass

    @abstractmethod
    def extract_category_page(self) -> list[Product | None]:
        """Function responsible for extracting products data from given category page."""
        pass

class ProductExtractor(Extractor):
    """
    Abstract Base Class for extracting data from single product pages.
    """
    @abstractmethod
    def extract_product_data(self) -> Product:
        pass


class SitemapExtractor(Extractor):
    """
    Abstract Base Class for extracting data from SitemapContent objects.
    """
    def __init__(self, sitemap_content: SitemapContent):
        self.sitemap_content = sitemap_content

    def extract_categories(self) -> list[str]:
        """Method responsible for extracting categories from sitemap. """
        ns = {'s': "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = self.sitemap_content.xml_tree.xpath('//s:url/s:loc', namespaces=ns)
        sitemap_urls = []
        for url in urls:
            sitemap_urls.append(url.text)
        return sorted(sitemap_urls)

    @staticmethod
    def filter_categories(categories: list[str]) -> list[str]:
        """Method responsible for filtering and deduplicating list of categories' paths. """
        filtered_categories = []
        for url in categories:
            url_ok = True
            for compared_url in categories:
                if compared_url.startswith(url + "/"):
                    url_ok = False
                    break
            if url_ok:
                filtered_categories.append(url)
        return filtered_categories
