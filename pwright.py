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
        self.page_content = self.PageContent(url)

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
            self.response: Response = page.goto(self.page_content.url)
        except TimeoutError:
            self.response_error = "Connection Timeout"
        except Error as e:
            print(e.message)

        if self.response is not None:
            self.page_content.status = self.response.status
            self.page_content.headers = self.response.headers
            self.page_content.body = self.response.body()
            try:
                self.page_content.raw_html = self.response.text()
            except UnicodeDecodeError:
                self.page_content.text = self.response.body().decode("utf-8", errors="ignore")

        # if self.render_javascript:
        #     self.metrics = cdp_session.send("Performance.getMetrics")

        self.browser.close()

    def run(self):
        self.create_browser()
        self.visit_page()
        self.page_content.build_content()

    @dataclass
    class PageContent:
        """
        Class representing actual content of the page build from its response
        """
        url: str
        status: Optional[str | int] = None
        headers: Optional[dict] = None
        body: Optional[str] = None
        text: Optional[str] = None

        title: Optional[str] = None
        raw_html: Optional[str] = None
        html_tree: Optional[etree.ElementTree] = None

        def build_content(self):
            self.normalize_html()
            self.build_html_tree()
            self.get_title()

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

        def count_h1(self):
            pass

        def count_imgs(self):
            pass


if __name__ == '__main__':
    my_url = PlayScraper(url=URL, render_javascript=False)
    my_url.run()
    print(my_url.page_content.headers)
    # print(my_url.page_content.raw_html)
    print(my_url.page_content.encoding)
    print(my_url.page_content.title)
