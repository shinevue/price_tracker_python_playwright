import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Optional
from urllib.parse import unquote

import lxml
from lxml import html
from lxml import etree
from playwright.sync_api import sync_playwright, TimeoutError, Response, Error

import utils
from const import ME
from exceptions import UnmatchingPrices
from logger import Log


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

log = Log()


class Visitor:
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

    def run(self, mode: str = 'default'):
        self.create_browser()
        self.visit_page()
        if mode == 'default':
            self.content.normalize_html()
            self.content.build_html_tree()
            self.content.get_title()
        elif mode == 'sitemap':
            print('sitemap')
            self.content.parse_sitemap()

    def create_browser(self):
        """ Create browser and context instances """
        self.browser = self.playwright.chromium.launch(args=BROWSER_SETTINGS, headless=True)
        self.context = self.browser.new_context(proxy=None,
                                                java_script_enabled=self.render_javascript,
                                                extra_http_headers=REQUEST_HEADERS)

    def visit_page(self):
        """ Use playwright tools to go to requested page and gather data, then assign to Url object """
        page = self.context.new_page()
        # cdp_session = self.context.new_cdp_session(page)
        try:
            self.response: Response = page.goto(self.content.url, wait_until='commit')
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

        # Sitemaps
        sitemap_urls: Optional[list[str]] = None

        def __repr__(self):
            return f'URL: {self.url}\n' \
                   f'Status code: {self.status}\n' \
                   f'Page Title: {self.title}\n' \
                   f'Encoding: {self.encoding}\n' \


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

        def parse_sitemap(self):
            ns = {'s': "http://www.sitemaps.org/schemas/sitemap/0.9"}
            parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
            xml_tree = etree.fromstring(self.raw_html.encode('utf-8'), parser=parser)
            urls = xml_tree.xpath('//s:url/s:loc', namespaces=ns)
            sitemap_urls = []
            for url in urls:
                sitemap_urls.append(url.text)
            self.sitemap_urls = sorted(sitemap_urls)

        def parse_product_data(self, site):
            """ """
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
            product_codes = []
            try:
                product_codes = self.html_tree.xpath('''/html/head/meta[@property='product:skusPage']/@content''')[0].split(',')
            except IndexError:
                print("No product codes found.")
                pass
            product_boxes = self.html_tree.xpath(site.XPathSelectors['product_container_category_page'])

            assert len(product_codes) == len(product_boxes), f'product codes lenghts doesnt match number of products for site {site}'

            print('product codes:', product_codes)
            print('product codes len:', len(product_codes))

            empty_prices, coupon_prices, normal_prices = 0, 0, 0
            for index, pc in enumerate(product_boxes):
                product_url, product_name, product_price = [], [], []
                try:
                    try:
                        product_url: list = pc.xpath(site.XPathSelectors['product_url_category_page'])[0]
                    except Exception as e:
                        log.write(f'no product URL found at product #{index}')
                        print('exception:', e)
                    try:
                        product_name = pc.xpath(site.XPathSelectors['product_name_category_page'])[0].strip()
                    except Exception as e:
                        log.write(f'no product name found at product #{index}')
                        print('exception:', e)
                    try:
                        product_price: list = pc.xpath(site.XSelector.CategoryPage.price)
                        normal_prices += 1 if product_price else normal_prices
                        if not product_price:
                            product_price: list = pc.xpath(site.XSelector.CategoryPage.price_with_code)
                            coupon_prices += 1 if product_price else coupon_prices
                            print(f'price after 2 selector: {product_price}')
                        else:
                            empty_prices += 1
                    except Exception as e:
                        log.write(f'no price found at product #{index}')
                        print('exception:', e)

                    msg = f"""Found prices: \n Normal: {normal_prices}\n Coupon: {coupon_prices}\n Empty: {empty_prices}\n"""
                    log.write(msg)
                    print(msg)

                except Exception as e:
                    print(f"error at {self.url}")
                    print('exception:', e)

                result.append({'product_name': product_name,
                               'product_code': product_codes[index],
                               'price': product_price,
                               'url': product_url})
            return result

        def parse_max_pagination_from_category_page(self, site):
            limit = self.html_tree.xpath(site.XPathSelectors['category_page_pagination_limit'])
            if len(limit) == 0:
                return 1
            return limit[0]
