import unicodedata
import posixpath
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Optional, Any
from urllib.parse import unquote

import lxml
from lxml import html
from lxml import etree
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings
from lxml.html.clean import Cleaner
from urllib.parse import urlparse

import utils
from const import ME
from exceptions import UnmatchingPrices

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']

REQUEST_HEADERS = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding':
        'gzip, deflate',
    'Accept-Language':
        'en-US,en;q=0.5',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}


class PlayScraper:
    """
    Main outer class for the scraper using Playwright
    """
    playwright = sync_playwright().start()
    browser = None
    context = None
    html_cleaner = None
    response_error = None
    response: Optional[Response] = None

    def __init__(self, url, render_javascript: bool = False):
        self.render_javascript = render_javascript
        self.metrics = None
        self.content = self.Content(url)

    def run(self):
        self.create_browser()
        self.visit_page()
        self.content.normalize_html()
        self.content.build_html_tree()
        self.content.get_title()

    def create_browser(self):
        """ Create browser and context instances """
        self.browser = self.playwright.chromium.launch(args=BROWSER_SETTINGS, headless=False)
        self.context = self.browser.new_context(proxy=None,
                                                java_script_enabled=self.render_javascript,
                                                extra_http_headers=REQUEST_HEADERS)

    def visit_page(self):
        """ Use playwright tools to go to requested page and gather data, then assign to Url object """
        page = self.context.new_page()
        # cdp_session = self.context.new_cdp_session(page)
        try:
            self.response: Response = page.goto(self.content.url)
        except TimeoutError:
            self.response_error = "Connection Timeout"
        except Error as e:
            print(e.message)

        if self.response.status == 403:
            print("403 Error occured.")

        if self.response is not None:
            self.content.status = self.response.status
            self.content.headers = self.response.headers
            self.content.body = self.response.body()
            try:
                self.content.raw_html = self.response.text()
            except UnicodeDecodeError:
                self.content.text = self.response.body().decode("utf-8", errors="ignore")

        self.browser.close()

    @dataclass
    class Content:
        """
        Class representing actual content of the page build from its response
        """

        # Page metadata and raw content
        url: str
        status: Optional[str | int] = None
        headers: Optional[dict] = None
        body: Optional[str] = None
        text: Optional[str] = None

        # HTML constructs for parsing data
        raw_html: Optional[str] = None
        html_tree: Optional[etree.ElementTree] = None

        # Basic page data
        domain: Optional[str] = None
        title: Optional[str] = None
        h1_text: Optional[str] = None
        h1_count: Optional[int] = None
        h2_count: Optional[int] = None
        h3_count: Optional[int] = None
        h4_count: Optional[int] = None
        hreflang_count: Optional[int] = None
        link_count: Optional[int] = None

        # Site specific data
        product_name: Optional[str] = None
        price: Optional[float] = None
        product_categories: Optional[tuple[str]] = None

        def __repr__(self):
            return f'URL: {self.url}\n' \
                   f'Status code: {self.status}\n' \
                   f'Page Title: {self.title}\n' \
                   f'Encoding: {self.encoding}\n' \
                   f'H1: {self.h1_text}\n' \
                   f'H1s: {self.h1_count}, H2s: {self.h2_count}, Links: {self.link_count}\n'

        @property
        def encoding(self):
            content_type = self.headers['content-type'].split(';')
            try:
                encoding = content_type[1].strip().split('=')[1].strip()
                return 'latin1' if encoding == 'latin-1' else encoding
            except IndexError:
                return None

        def normalize_html(self):
            if self.raw_html:
                self.raw_html = unicodedata.normalize("NFKC", unquote(self.raw_html.strip()))  # encoding=self.page_encoding

        def build_html_tree(self):
            # Maybe forcing encoding is not the best way?
            # temp_bytes = self.raw_html.encode(encoding=self.encoding, errors='backslashreplace')

            tree_parser = html.HTMLParser(remove_comments=True, recover=True)
            self.html_tree = lxml.html.fromstring(self.raw_html, parser=tree_parser)

        def parse_product_data(self, site):
            self.parse_prices(site)
            self.parse_product_name(site)
            self.parse_product_category()

        def parse_categories(self, xpath_selector: str):
            categories = self.html_tree.xpath(xpath_selector)
            return categories

        def format_for_sheets(self):
            return [self.domain, datetime.strftime(datetime.now(), '%Y-%m-%d, %H:%M:%S'), self.product_name, self.price, self.url]

        def get_title(self):
            if len(self.html_tree.xpath("//title[1]//text()")) > 0:
                self.title = " ".join(unquote(str(self.html_tree.xpath("//title[1]//text()")[0])).split()).strip()

        def get_h1_text(self):
            self.h1_text = unicodedata.normalize("NFKC", unquote(str(self.html_tree.xpath("normalize-space(//h1)"))))

        def parse_product_category(self):
            url_parts = PurePosixPath(unquote(self.url)).parts
            self.product_categories = PurePosixPath(unquote(self.url)).parts[2:]
            self.domain = url_parts[1]

        def parse_products_from_category(self, site):
            return self.html_tree.xpath(site.XPathSelectors['product_url'])

        def parse_product_name(self, site):
            self.product_name = self.html_tree.xpath(site.XPathSelectors['product_name'])[0]

        def parse_prices(self, site):
            prices_found = self.html_tree.xpath(site.XPathSelectors['main_price'])
            if prices_found:
                if utils.compare_list_elements(prices_found):
                    self.price = float(prices_found[0][:-2] + '.' + prices_found[0][-2:])
                else:
                    print('prices_found: ', prices_found)
                    raise UnmatchingPrices

        def parse_prices_from_category_page(self, site):
            result = []
            for pc in self.html_tree.xpath(site.XPathSelectors['product_container_category_page']):
                try:
                    product_url = pc.xpath(site.XPathSelectors['product_url_category_page'])[0]
                    product_name = pc.xpath(site.XPathSelectors['product_name_category_page'])[0].strip()
                    product_price = pc.xpath(site.XPathSelectors['price_category_page'])[0]
                    result.append({'product_name': product_name,
                                   'price': product_price,
                                   'url': product_url})
                except:
                    continue
            return result

        def parse_max_pagination_from_category_page(self, site):
            return self.html_tree.xpath(site.XPathSelectors['category_page_pagination_limit'])
