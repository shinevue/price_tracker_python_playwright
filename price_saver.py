import os
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

import utils
import database.models as m

from database import sheets, db
from const import ME
from scraper import PlayScraper

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"


def me_scrape_price_from_product_page(paths_list: list[str] = None,
                                      paths_are_absolute: bool = True,
                                      target_db: str = 'google_sheets'):
    """ Use list of paths to scrape prices directly from the single product pages. """

    url_limit = 50
    if not paths_list:
        try:
            paths_list = utils.read_urls('urls.txt')
        except:
            pass

    for path in paths_list[:url_limit]:
        full_url = path if paths_are_absolute else ME.DOMAIN + path
        scraper = PlayScraper(url=full_url, render_javascript=True)
        scraper.run()
        scraper.content.parse_product_data(site=ME)

        match target_db:
            case 'google_sheets':
                creds = sheets.authorize_google()
                if creds:
                    sheets.append_to_sheets(creds=creds,
                                            spreadsheet_id=SPREADSHEET_ID,
                                            range_name=RANGE_NAME,
                                            value_input_option="USER_ENTERED",
                                            values=[scraper.content.format_for_sheets()])
            case 'database':
                pass
            case other:
                print(scraper.content.format_for_sheets())


def me_scrape_prices_from_category_page(category_id: int,
                                        session: Session = db.session):
    """ Scrape all products data including prices from a given category already stored in the database."""

    stmt = select(m.MECategories).where(m.MECategories.id == category_id)
    category_obj = session.scalars(stmt).first()
    category_path = category_obj.category_path
    print(category_path)
    page = 1
    full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
    print(f'full path {full_path}')
    scraper = PlayScraper(url=full_path, render_javascript=True)
    scraper.run()
    max_pages = int(scraper.content.parse_max_pagination_from_category_page(site=ME))
    data = scraper.content.parse_prices_from_category_page(site=ME)
    if max_pages > 1:
        while page <= max_pages:
            page += 1
            full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
            scraper = PlayScraper(url=full_path, render_javascript=True)
            scraper.run()
            data.extend(scraper.content.parse_prices_from_category_page(site=ME))

    for item in data:
        product_obj = m.MEProducts(product_name=item['product_name'],
                                   category_id=category_id)
        price_obj = m.MEPrices(price=item['price'],
                               url=item['url'])
        product_obj.prices.append(price_obj)
        db.session.add(product_obj)
    category_obj.last_crawl = datetime.now()
    db.session.commit()
