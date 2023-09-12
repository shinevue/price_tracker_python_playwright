from dotenv import load_dotenv

import crawler
import price_saver
from database import db

load_dotenv()


if __name__ == '__main__':
    # scrape()
    # crawler.me_crawl_for_categories()
    crawler.me_crawl_for_categories()
    # paths = crawler.me_crawl_category_for_products()
    # price_saver.me_scrape_price(paths_list=paths)
    # db.test_db()
