import os

import utils
import sheets
from dotenv import load_dotenv

from crawler import me_crawl
from scraper import PlayScraper
from price_saver import scrape

load_dotenv()


if __name__ == '__main__':
    scrape()
    # me_crawl()
