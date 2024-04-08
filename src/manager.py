import time
from src.base.extractor_base import PageContent

import browser
from src.me.extractor_me import MECategoryExtractor


class Manager:
    def scrape_full_category(
        self,
        category_url: str,
        max_pages: int = 0,
        timeout: int = 5,
        render_javascript: bool = False,
    ) -> list:
        url = category_url + "?limit=50"
        b = browser.Browser(render_javascript=render_javascript)
        page: PageContent | None = b.visit_url(url=url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            raise Exception("Error while accessing page")

        extractor = MECategoryExtractor(page)
        max_pagination = extractor.extract_max_pagination()

        # Request the first page
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
                # b = Browser(render_javascript=render_javascript)
                url = category_url + f"?limit=50&page={page_count}"
                page: PageContent | None = b.visit_url(url=url)

                if not page:
                    print("No page in response. Error: ")
                    print(b.response_error)
                    continue

                extractor = MECategoryExtractor(page)
                products.extend(extractor.extract_category_page())

        return products
