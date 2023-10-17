import time
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from dotenv import load_dotenv
from sqlalchemy.sql.functions import func
from sqlalchemy import update

import scraper
from database import db, models as m
from logger import Log

load_dotenv()
log = Log()


def check_manager(session: Session = db.session,
                  save_results: bool = False,
                  categories_limit: int = 1,
                  delay: int = 5) -> None:
    """
    Searches database for categories for check based on 'regular_check' column and specified time interval in days.
    :param session: SQLAlchemy database session
    :param bool save_results: If True, will save results to database.
    :param int categories_limit: Number of categories to scrape in current run.
    :param delay: Seconds to wait between page visits.

    """

    # Search for categories
    q = (select(m.MECategories.id)
         .where(and_(m.MECategories.regular_check,
                     or_((m.MECategories.last_check + func.make_interval(0, 0, 0, m.MECategories.check_freq) <= datetime.now()),
                         m.MECategories.last_check == None)))
         .order_by(m.MECategories.last_check.desc())
         .limit(categories_limit))
    category_ids = session.scalars(q).all()

    for cat_id in category_ids:
        print(f"Starting scraping prices for category {cat_id}...")
        scraper.me_prices_from_category(category_id=cat_id, save_results=False)
        time.sleep(5)

        if save_results:
            print("Saving to database...")
            q = (update(m.MECategories).where(m.MECategories.id == cat_id)).values(last_check=datetime.now())
            session.execute(q)


if __name__ == '__main__':
    check_manager(save_results=False,
                  categories_limit=1,
                  delay=2)
