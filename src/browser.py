from playwright.sync_api import sync_playwright, Response, TimeoutError

from src.base.extractor_base import PageContent


class Browser:
    """
    Main outer class for the scraper using Playwright
    """

    BROWSER_SETTINGS = [
        "--headless=new",
        "--deny-permission-prompts",
        "--disable-notifications",
        "--disable-gpu",
    ]
    REQUEST_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
    }
    playwright = sync_playwright().start()
    html_cleaner = None
    response_error = None

    def __init__(self, render_javascript: bool = False):
        self.render_javascript = render_javascript
        self.browser = self.playwright.chromium.launch(
            args=self.BROWSER_SETTINGS, headless=True
        )
        self.context = self.browser.new_context(
            proxy=None,
            java_script_enabled=self.render_javascript,
            extra_http_headers=self.REQUEST_HEADERS,
        )

    def visit_url(self, url: str) -> PageContent | None:
        """Visit the given URL"""
        page = self.context.new_page()
        try:
            response: Response | None = page.goto(url, wait_until="commit")
            if not response:
                page.screenshot(path=f"screenshot_{url}.png")
                self.response_error = "No response"
                return None
            if response.status != 200:
                self.response_error = f"Error: {response.status}"
                return None
            return PageContent(
                url, response.status, response.headers, response.body(), response.text()
            )
        except TimeoutError:
            self.response_error = "Connectrion Timeout"
            return None
        except Exception as e:
            print(e)
            self.response_error = e

        self.browser.close()
