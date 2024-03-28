import time
from src.base.extractor_base import CategoryExtractor
from src.base.site_base import Site
from src.me.extractor_me import MECategoryScraper


class Manager:
    def __init__(self, site: Site, category_extractor: CategoryExtractor):
        self.ce = site.category_extractor

    def scrape_categories(self, max_pages: int = 0):
        timeout = 5
        base_path = 
        max_pagination = int(self.ce.extract_max_pagination())

        # Request the first page
        page_count = 0
        products = self.ce.extract_products_data()
        if products:
            page_count += 1
        if max_pagination > 1 and not max_pages:
            while page_count <= max_pagination:
                time.sleep(timeout)
                page_count += 1
                print(f"Page {page_count}...")

