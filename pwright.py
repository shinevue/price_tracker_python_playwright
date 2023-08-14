import unicodedata
from dataclasses import dataclass
from typing import Optional, Any
from urllib.parse import unquote

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings
from lxml.html.clean import Cleaner

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']


@dataclass
class PageContent:
    """
    Class representing actual content of the page build from its response
    """
    url: str
    title: Optional[str] = None
    page_encoding: Optional[str] = None
    raw_html: Optional[str] = None
    html_tree: Optional[str] = None

    def normalize_html(self):
        if self.raw_html:
            self.html_tree = unicodedata.normalize("NFKC", unquote(self.raw_html.strip()))    # encoding=self.page_encoding
            print(self.html_tree)

    def build_html_tree(self):
        pass

    def count_h1(self):
        pass

    def count_imgs(self):
        pass


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
    content: Optional[PageContent] = None

    def set_url_content(self):
        self.content = PageContent(url_obj_1.url)
        self.content.raw_html = url_obj_1.text
        self.content.normalize_html()



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

    def __init__(self, url_obj: Url, render_javascript: bool = False):
        self.url_obj = url_obj
        self.render_javascript = render_javascript
        self.metrics = None

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


if __name__ == '__main__':
    url_obj_1 = Url('https://onet.pl')
    url1 = PlayScraper(url_obj=url_obj_1, render_javascript=False)
    url1.run()
    print(url_obj_1.status)
    print(url_obj_1.headers)
    url_obj_1.set_url_content()

