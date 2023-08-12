from dataclasses import dataclass
from typing import Optional, Any

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings
from lxml.html.clean import Cleaner

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']


@dataclass
class UrlContent:
    """
    Class representing actual content of the page build from its response
    """
    title: str
    raw_html: str


@dataclass
class Url:
    """
    Class representig general URL data, independent from its actual content
    """
    url: str
    status: str | int
    headers: dict
    body: str
    text: str
    content: Optional[UrlContent] = UrlContent


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
        """ Use playwright tools to go to requested page and gather data """
        page = self.context.new_page()
        # cdp_session = self.context.new_cdp_session(page)
        try:
            self.response = page.goto(self.url_obj.url)
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

    def build_html_tree(self):
        pass

    def run(self):
        self.create_browser()
        self.visit_page()
        print(self.url_obj.headers)
        print(self.metrics)


if __name__ == '__main__':
    url_obj_1 = Url('https://onet.pl')
    url1 = PlayScraper(url_obj=url_obj_1, render_javascript=False)
    url1.run()
