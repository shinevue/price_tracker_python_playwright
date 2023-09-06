from dotenv import load_dotenv

from crawler import me_crawl_for_urls
from database import db

load_dotenv()


if __name__ == '__main__':
    # scrape()
    # me_crawl_for_urls()
    db.test_db()
