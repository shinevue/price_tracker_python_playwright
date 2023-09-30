import os
from datetime import datetime

import time
from sqlalchemy import select

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

import utils
from const import ME
from database import db, models, sheets, models as m
from engine import PlayScraper

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"


def me_crawl_categories(site=ME,
                        session: Session = db.session):
    ps = PlayScraper(url=site.DOMAIN, render_javascript=True)
    ps.run()
    categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['category_list'])
    inner_categories = []
    for category in categories:
        ps = PlayScraper(url=site.DOMAIN + category, render_javascript=True)
        ps.run()
        inner_categories.extend(path for path in ps.content.parse_categories(xpath_selector=site.XPathSelectors['inner_categories']) if path not in inner_categories)
    inner_categories.sort(reverse=True)
    filtered_categories = []
    for cat in inner_categories:
        if not any(existing_path.startswith(cat) for existing_path in filtered_categories):
            filtered_categories.append(cat)
    for filcat in filtered_categories:
        session.add(models.MECategories(category_path=filcat,
                                        time_discovered=datetime.now()))
    session.commit()


def me_crawl_category_for_products(category_path: str, site=ME):
    ps = PlayScraper(url=site.DOMAIN + category_path)
    ps.run()
    products_paths = ps.content.parse_products_from_category(site)
    return products_paths


def parse_sitemap_categories(site=ME,
                             session: Session = db.session):
    """ Parse categories from the XML sitemap. The most reliable and accurate way of scraping for categories. """
    ps = PlayScraper(url=site.CATEGORY_SITEMAP_URL)
    ps.run(mode='sitemap')
    urls = ps.content.sitemap_urls

    filtered_categories = []
    for url in urls:
        url_ok = True
        for compared_url in urls:
            if compared_url.startswith(url + "/"):
                url_ok = False
                break
        if url_ok:
            filtered_categories.append(url)
    for filcat in filtered_categories:
        session.add(models.MECategories(category_path=filcat[len(site.DOMAIN):],
                                        time_discovered=datetime.now()))
    session.commit()


def me_price_from_product(paths_list: list[str] = None,
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


def me_prices_from_category(category_id: int,
                            all_pages: int = False,
                            save_results: bool = False,
                            session: Session = db.session):
    """ Scrape all products data including prices from a given category already stored in the database."""

    # Find category data
    q = select(m.MECategories).where(m.MECategories.id == category_id)
    category_obj = session.scalars(q).first()
    category_path = category_obj.category_path
    print(category_path)

    # Set starting variables
    page = 1
    full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
    print(f'full path {full_path}')

    # Run browser
    ps = PlayScraper(url=full_path, render_javascript=True)
    ps.run()

    # Parse data
    max_pagination = int(ps.content.parse_max_pagination_from_category_page(site=ME))  # Pagination total pages
    data = ps.content.parse_prices_from_category_page(site=ME)
    print(data)

    # Visit next pages of category
    if max_pagination > 1 and all_pages:
        while page <= max_pagination:
            time.sleep(10)

            page += 1
            full_path = ME.DOMAIN + category_path + f"?limit=50&page={page}"
            ps = PlayScraper(url=full_path, render_javascript=True)
            ps.run()
            data.extend(ps.content.parse_prices_from_category_page(site=ME))

    # Insert into database:
    if save_results:
        for item in data:
            print(item)
            product_obj = m.MEProducts(product_name=item['product_name'],
                                       product_code=item['product_code'],
                                       path=item['url'],
                                       category_id=category_id)
            price_obj = m.MEPrices(price=item['price'])
            product_obj.prices.append(price_obj)
            session.add(product_obj)
    category_obj.last_crawl = datetime.now()
    session.commit()

    # if save_results:
    #     for item in data:
    #         print(item)
    #         # product_obj = m.MEProducts(product_name=item['product_name'],
    #         #                            product_code=item['product_code'],
    #         #                            path=item['url'],
    #         #                            category_id=category_id)
    #         # price_obj = m.MEPrices(price=item['price'])
    #
    #         insert_st = insert(m.MEProducts).values(product_name=item['product_name'],
    #                                                 product_code=item['product_code'],
    #                                                 path=item['url'],
    #                                                 category_id=category_id,
    #                                                 last_update=datetime.now())
    #         update_st = insert_st.on_conflict_do_update(constraint='me_products_pk',
    #                                                     set_=dict(last_update=datetime.now()))
    #         print(update_st)
    #         session.execute(update_st)
    #         result = session.scalars(update_st.returning(m.MEProducts.id), execution_options={'populate_existing': True})
    #         print(result.first())
