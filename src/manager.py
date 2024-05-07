import time
from src.base.extractor_base import PageContent, SitemapContent, SitemapExtractor

import browser
from src.me.extractor_me import MECategoryExtractor


class Manager:
    def __init__(self, site: str):
        match site:
            case "ME":
                self.extractor = MECategoryExtractor
                self.sitemap_extractor = SitemapExtractor
            case _:
                raise Exception("Site not supported")

    def scrape_full_category(
        self,
        category_url: str,
        max_pages: int = 0,
        timeout: int = 5,
        render_javascript: bool = False,
    ) -> list:
        url = category_url + "?limit=50"
        # Initialize the browser
        b = browser.Browser(render_javascript=render_javascript)
        # Request the first page
        page: PageContent | None = b.visit_url(url=url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            raise Exception("Error while accessing page")
        extractor = self.extractor(page)
        max_pagination = extractor.extract_max_pagination()
        page_count = 0
        products = extractor.extract_category_page()
        if products:
            page_count += 1
        if max_pagination > 1 and not max_pages:
            # Iterate through the rest of the pages
            while page_count <= max_pagination:
                time.sleep(timeout)
                page_count += 1
                print(f"Page {page_count}...")
                url = category_url + f"?limit=50&page={page_count}"
                page: PageContent | None = b.visit_url(url=url)
                if not page:
                    print("No page in response. Error: ")
                    print(b.response_error)
                    continue
                extractor = self.extractor(page)
                products.extend(extractor.extract_category_page())
        return products

    def parse_sitemap_categories(
        self,
        sitemap_url: str
        ):
        """ Parse categories from the XML sitemap. The most reliable and accurate way of scraping for categories. """
        b = browser.Browser()
        sitemap_content = b.visit_url(sitemap_url)
        if not sitemap_content:
            raise Exception("Error while accessing sitemap")
        category_urls = self.sitemap_extractor.extract_categories(sitemap_content)
        if not category_urls:
            raise Exception("No categories found in sitemap")
        filtered_categories = self.sitemap_extractor.filter_categories(category_urls)

        return filtered_categories

