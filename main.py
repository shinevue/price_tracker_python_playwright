from dotenv import load_dotenv

from crawler import me_crawl_for_categories
from database import db

load_dotenv()


if __name__ == '__main__':
    # scrape()
    me_crawl_for_categories()
    # db.test_db()
