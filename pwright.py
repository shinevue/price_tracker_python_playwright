from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError, Response, Error, Request, CDPSession, \
    Route, ProxySettings

BROWSER_SETTINGS = ['--headless=new',
                    '--deny-permission-prompts',
                    '--disable-notifications',
                    '--disable-gpu']

url_to_check = 'https://onet.pl'


class UrlData:
    def __init__(self, url):
        self.url = url

    def visit_page(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(args=BROWSER_SETTINGS, headless=False)
        page = browser.new_page()
        page.goto(self.url)
        print(page.title())
        browser.close()


if __name__ == '__main__':
    url1 = UrlData(url_to_check)
    url1.visit_page()
