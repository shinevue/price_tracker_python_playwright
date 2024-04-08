from functools import wraps
import browser
from src.base.product_base import Product
from src.base.extractor_base import PageContent
from src.me.extractor_me import MECategoryExtractor, MEProductExtractor

import time
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from sqlalchemy.sql.functions import func
from sqlalchemy import update

from database import db, models as m
from logger import Log

log = Log()


urls = [
    "https://en.wikipedia.org/wiki/Security_orchestration",
    "https://en.wikipedia.org/wiki/Security_information_and_event_management",
    "https://en.wikipedia.org/wiki/Security_architecture",
    "https://en.wikipedia.org/wiki/Python",
]


def product_page_scrape(urls: list):
    b = browser.Browser()
    for url in urls:
        print(f"Visiting page - {url}")
        page: PageContent | None = b.visit_url(url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            continue
        print("visited url: ", page.url)
        print("status code: ", page.status_code)
        print("test fragment of html_tree: ", page.html_tree[:150])

        print("Running Product Scraper")
        product: Product = MEProductExtractor(page_content=page).extract_product_data()
        print(product)
        print(product.name)
        print(product.price)
        print("-" * 16)


def category_page_scrape(urls: list):
    b = browser.Browser(render_javascript=True)
    for url in urls:
        print(f"Visiting category page - {url}")

        page: PageContent | None = b.visit_url(url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            continue

        print("visited url: ", page.url)
        print("status code: ", page.status_code)
        print("test fragment of html_tree: ", page.html_tree[:150])

        result = MECategoryExtractor(page_content=page).extract_category_page()
        for item in result:
            if item:
                print(item.url)
                print(item.name)
                print(item.product_code)
                print(item.price)


def check_manager(
    session: Session = db.session,
    save_results: bool = False,
    categories_limit: int = 1,
    delay: int = 5,
) -> None:
    """
    Searches database for categories for check based on 'regular_check' column and specified time interval in days.
    :param session: SQLAlchemy database session
    :param bool save_results: If True, will save results to database.
    :param int categories_limit: Number of categories to scrape in current run.
    :param delay: Seconds to wait between page visits.
    """

    # Search for categories
    q = (
        select(m.MECategories.id)
        .where(
            and_(
                m.MECategories.regular_check,
                or_(
                    (
                        m.MECategories.last_check
                        + func.make_interval(0, 0, 0, m.MECategories.check_freq)
                        <= datetime.now()
                    ),
                    m.MECategories.last_check == None,
                ),
            )
        )
        .order_by(m.MECategories.last_check.desc())
        .limit(categories_limit)
    )
    category_ids = session.scalars(q).all()

    for cat_id in category_ids:
        print(f"Starting scraping prices for category {cat_id}...")
        #  TODO Run scraping
        time.sleep(delay)

        if save_results:
            print("Saving to database...")
            q = (
                update(m.MECategories)
                .where(m.MECategories.id == cat_id)
                .values(last_check=datetime.now())
            )
            session.execute(q)
            session.commit()


if __name__ == "__main__":
    product_page_scrape(
        urls=[
            "https://www.mediaexpert.pl/gaming/playstation-5/konsole-ps5/konsola-sony-playstation-5-slim"
        ]
    )
    category_page_scrape(
        urls=[
            "https://www.mediaexpert.pl/agd-do-zabudowy/akcesoria-do-zabudowy/filtry-do-okapow-do-zabudowy"
        ]
    )
