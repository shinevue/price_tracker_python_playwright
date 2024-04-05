import time
from src.base.site_base import Site


class Manager:
    def __init__(self, site: Site):
        self.site = site

    def scrape_categories(self, max_pages: int = 0):
        timeout = 5
        # base_path =  self.site.DOMAIN
        max_pagination = int(self.site.category_extractor.extract_max_pagination())

        # Request the first page
        page_count = 0
        products = self.site.category_extractor.extract_products_data()
        if products:
            page_count += 1
        if max_pagination > 1 and not max_pages:
            while page_count <= max_pagination:
                time.sleep(timeout)
                page_count += 1
                print(f"Page {page_count}...")

