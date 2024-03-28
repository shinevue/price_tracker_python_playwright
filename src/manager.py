import time
from src.base.scraper_base import CategoryExtractor
from src.me.scraper_me import MECategoryScraper

class Manager:
    def __init__(self, category_scraper: CategoryExtractor):
        self.category_scraper = category_scraper
    def scrape_categories(self, max_pages: int = 0):
        timeout = 5
        max_pagination = int(self.category_scraper.extract_max_pagination())

        # Request the first page
        page_count = 0
        products = self.category_scraper.extract_products_data()
        if products:
            page_count += 1
        if max_pagination > 1 and not max_pages:
            time.sleep(timeout)
            page_count += 1
            print(f"Page {page}...")
            


        pass
