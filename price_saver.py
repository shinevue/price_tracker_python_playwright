import os
from sqlalchemy import select
from sqlalchemy.orm import Session

import utils
import database.models as m

from database import sheets, db
from const import ME
from scraper import PlayScraper

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"
URL_LIMIT = 50


def me_scrape_price_from_product_page(paths_list: list[str] = None):
    if not paths_list:
        try:
            paths_list = utils.read_urls('urls.txt')
        except:
            pass

    for path in paths_list[:URL_LIMIT]:
        scraper = PlayScraper(url=ME.DOMAIN + path, render_javascript=True)
        scraper.run()
        scraper.content.parse_product_data(site=ME)

        creds = sheets.authorize_google()
        if creds:
            sheets.append_to_sheets(creds=creds,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    range_name=RANGE_NAME,
                                    value_input_option="USER_ENTERED",
                                    values=[scraper.content.format_for_sheets()])


def me_scrape_prices_from_category_page(category_id: int,
                                        session: Session = db.session):
    stmt = select(m.MECategories).where(m.MECategories.id == category_id)
    category_path = session.scalars(stmt).first().category_path

    page = 1
    full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
    scraper = PlayScraper(url=full_path, render_javascript=True)
    scraper.run()
    max_pages = int(scraper.content.parse_max_pagination_from_category_page(site=ME)[0])
    data = scraper.content.parse_prices_from_category_page(site=ME)
    # if max_pages > 1:
    #     while page <= max_pages:
    #         page += 1
    #         full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
    #         scraper = PlayScraper(url=full_path, render_javascript=True)
    #         scraper.run()
    #         data.extend(scraper.content.parse_prices_from_category_page(site=ME))
    print('DATA SUMMARY\n')
    print(f"pagination pages - {max_pages}")
    print(f'found products - {len(data)}')
    print(data)
    #
    for item in data:
        product_obj = m.MEProducts(product_name=item['product_name'],
                                   category_id=category_id)
        price_obj = m.MEPrices(price=item['price'],
                               url=item['url'])
        product_obj.prices.append(price_obj)
        db.session.add(product_obj)
    db.session.commit()

