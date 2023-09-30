import time
from argparse import ArgumentParser
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session


from dotenv import load_dotenv

import engine
import scraper
from database import db, models as m

load_dotenv()


def main_arg(mode: str, domain: Optional[str], paths_source: Optional[str]):
    match mode:
        case 'crawl_categories' | 'cc':
            if domain in ['mediaexpert', 'mediaexpert.pl', 'me']:
                scraper.me_crawl_categories()
            else:
                print('Domain not supported.')

        case 'scrape_prices' | 'sp':
            if paths_source == 'file':
                scraper.me_price_from_product()


def manager(session: Session = db.session):
    q = select(m.MECategories.id).where(m.MECategories.is_checked).order_by(m.MECategories.last_crawl.desc())
    category_ids = session.scalars(q).all()
    for cat_id in category_ids:
        print(f"Starting scraping prices for category {cat_id}")
        scraper.me_prices_from_category(category_id=cat_id)
        time.sleep(5)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-m', '--mode')
    parser.add_argument('-d', '--domain')
    parser.add_argument('-ps', '--paths-source')
    args = parser.parse_args()

    # main_arg(domain=args.domain, mode=args.mode, paths_source=args.paths_source)
    # scrape()
    # scraper.me_crawl_for_categories()
    # scraper.me_crawl_for_categories()
    # paths = scraper.me_crawl_category_for_products()
    # scraper.me_scrape_price(paths_list=paths)
    # scraper.me_prices_from_category(category_id=13879, save_results=True)
    # db.test_db()
    scraper.parse_sitemap_categories()
    # manager()
    # db.test_db()
