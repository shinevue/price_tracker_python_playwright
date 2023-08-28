import unicodedata
from dataclasses import dataclass
from typing import Optional, Any
from urllib.parse import unquote

import lxml
from lxml import html
from lxml import etree
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings
from lxml.html.clean import Cleaner

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']

URL = 'https://www.biznes.gov.pl/pl'


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

    def __init__(self, url: str, render_javascript: bool = False):
        self.render_javascript = render_javascript
        self.metrics = None
        self.content = self.Content(url)

    def create_browser(self):
        """ Create browser and context instances """
        self.browser = self.playwright.chromium.launch(args=BROWSER_SETTINGS, headless=False)
        self.context = self.browser.new_context(proxy=None,
                                                java_script_enabled=self.render_javascript)

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

        if self.response is not None:
            self.content.status = self.response.status
            self.content.headers = self.response.headers
            self.content.body = self.response.body()
            try:
                self.content.raw_html = self.response.text()
            except UnicodeDecodeError:
                self.content.text = self.response.body().decode("utf-8", errors="ignore")

        # if self.render_javascript:
        #     self.metrics = cdp_session.send("Performance.getMetrics")

        self.browser.close()

    def run(self):
        self.create_browser()
        self.visit_page()
        self.content.build_content()

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
        title: Optional[str] = None
        h1_text: Optional[str] = None
        h1_count: Optional[int] = None
        h2_count: Optional[int] = None
        h3_count: Optional[int] = None
        h4_count: Optional[int] = None
        hreflang_count: Optional[int] = None
        link_count: Optional[int] = None

        def __repr__(self):
            return f'URL: {self.url}\n' \
                   f'Page Title: {self.title}\n' \
                   f'Encoding: {self.encoding}' \
                   f'H1: {self.h1_text}\n' \
                   f'H1s: {self.h1_count}, H2s: {self.h2_count}, Links: {self.link_count}'

        def build_content(self):
            self.normalize_html()
            self.build_html_tree()
            self.get_title()
            self.count_items()

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

        def get_title(self):
            if len(self.html_tree.xpath("//title[1]//text()")) > 0:
                self.title = " ".join(unquote(str(self.html_tree.xpath("//title[1]//text()")[0])).split()).strip()

        def get_h1_text(self):
            self.h1_text = unicodedata.normalize("NFKC", unquote(str(self.html_tree.xpath("normalize-space(//h1)"))))

        def count_items(self):
            self.h1_count = len(self.html_tree.xpath("//h1"))
            self.h3_count = len(self.html_tree.xpath("//h3"))
            self.h2_count = len(self.html_tree.xpath("//h2"))
            self.h4_count = len(self.html_tree.xpath("//h4"))
            self.hreflang_count = len(self.html_tree.xpath("//link[@rel='alternate' and @hreflang]"))
            self.link_count = len(self.html_tree.xpath("//a"))

        def count_imgs(self):
            pass


if __name__ == '__main__':
    my_url = PlayScraper(url=URL, render_javascript=False)
    my_url.run()
    # print(my_url.page_content.raw_html)
    print(my_url.content)
