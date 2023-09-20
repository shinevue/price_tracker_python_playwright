from argparse import ArgumentParser
from typing import Optional

from dotenv import load_dotenv

import crawler
import price_saver
from database import db

load_dotenv()


def main_arg(mode: str, domain: Optional[str], paths_source: Optional[str]):
    match mode:
        case 'crawl_categories' | 'cc':
            match domain:
                case 'mediaexpert' | 'mediaexpert.pl' | 'me':
                    crawler.me_crawl_for_categories()
                case other:
                    print('Domain not supported.')

        case 'scrape_prices' | 'sp':
            match paths_source:
                case 'file':
                    price_saver.me_scrape_price_from_product_page()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-m', '--mode')
    parser.add_argument('-d', '--domain')
    parser.add_argument('-ps', '--paths-source')
    args = parser.parse_args()

    # main_arg(domain=args.domain, mode=args.mode, paths_source=args.paths_source)
    # scrape()
    # crawler.me_crawl_for_categories()
    # crawler.me_crawl_for_categories()
    # paths = crawler.me_crawl_category_for_products()
    # price_saver.me_scrape_price(paths_list=paths)
    price_saver.me_scrape_prices_from_category_page(category_id=10299)
    # db.test_db()
