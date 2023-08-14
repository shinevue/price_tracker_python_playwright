import unicodedata
from dataclasses import dataclass
from typing import Optional, Any
from urllib.parse import unquote

import lxml
from lxml import html
from lxml.etree import ElementTree
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
    Main worker class for the scraper using Playwright
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
        self.url_obj = self.Url(url)

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
            self.response: Response = page.goto(self.url_obj.url)
        except TimeoutError:
            self.response_error = "Connection Timeout"
        except Error as e:
            print(e.message)

        if self.response is not None:
            self.url_obj.status = self.response.status
            self.url_obj.headers = self.response.headers
            self.url_obj.body = self.response.body()
            try:
                self.url_obj.text = self.response.text()
            except UnicodeDecodeError:
                self.url_obj.text = self.response.body().decode("utf-8", errors="ignore")

        # if self.render_javascript:
        #     self.metrics = cdp_session.send("Performance.getMetrics")

        self.browser.close()

    def run(self):
        self.create_browser()
        self.visit_page()
        self.url_obj.set_url_content()
        self.url_obj.page_content.build_content()

    @dataclass
    class Url:
        """
        Class representing URL metadata & raw, unprocessed data
        """
        url: str
        status: Optional[str | int] = None
        headers: Optional[dict] = None
        body: Optional[str] = None
        text: Optional[str] = None

        def __init__(self, url):
            self.url = url
            self.page_content = self.PageContent()

        def set_url_content(self):
            self.page_content.raw_html = self.text

        @dataclass
        class PageContent:
            """
            Class representing actual content of the page build from its response
            """
            title: Optional[str] = None
            page_encoding: Optional[str] = None
            raw_html: Optional[str] = None
            html_tree: Optional[ElementTree] = None

            def build_content(self):
                self.normalize_html()
                self.build_html_tree()
                self.get_title()

            def normalize_html(self):
                if self.raw_html:
                    self.raw_html = unicodedata.normalize("NFKC", unquote(self.raw_html.strip()))  # encoding=self.page_encoding

            def build_html_tree(self):
                encoding = "latin1"
                temp_bytes = self.raw_html.encode(encoding, errors='backslashreplace')

                tree_parser = html.HTMLParser(remove_comments=True, recover=True)
                self.html_tree = lxml.html.fromstring(temp_bytes, parser=tree_parser)

            def get_title(self):
                if len(self.html_tree.xpath("//title[1]//text()")) > 0:
                    self.title = " ".join(unquote(str(self.html_tree.xpath("//title[1]//text()")[0])).split()).strip()

            def count_h1(self):
                pass

            def count_imgs(self):
                pass


if __name__ == '__main__':
    url1 = PlayScraper(url=URL, render_javascript=False)
    url1.run()
    print(url1.url_obj.page_content.title)

