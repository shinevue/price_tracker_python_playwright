from dataclasses import dataclass

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']


@dataclass
class UrlContent:
    title: str
    body: str
    raw_html: str


@dataclass
class UrlData:
    url: str
    url_content: UrlContent = None


class PlayScraper:
    def __init__(self, url: UrlData):
        self.url = url
        self.playwright = sync_playwright().start()
        self.browser = None

    def create_browser(self):
        self.browser = self.playwright.chromium.launch(args=BROWSER_SETTINGS, headless=False)

    def visit_page(self):
        page = self.browser.new_page()
        page.goto(self.url)
        self.browser.close()

    def run(self):
        self.create_browser()
        self.visit_page()


if __name__ == '__main__':
    url_obj = UrlData('https://onet.pl')
    url1 = PlayScraper(url_obj)
