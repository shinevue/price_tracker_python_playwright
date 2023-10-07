import time
from argparse import ArgumentParser
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from dotenv import load_dotenv
from sqlalchemy.sql.functions import now, func
from sqlalchemy import update

import engine
import scraper
from database import db, models as m, models

load_dotenv()


def check_manager(session: Session = db.session):
    q = (select(m.MECategories.id)
         .where(and_(m.MECategories.regular_check,
                     or_((m.MECategories.last_check + func.make_interval(0, 0, 0, m.MECategories.check_freq) <= datetime.now()),
                         m.MECategories.last_check == None)))
         .order_by(m.MECategories.last_check.desc())
         .limit(2))
    category_ids = session.scalars(q).all()
    for cat_id in category_ids:
        print(f"Starting scraping prices for category {cat_id}")

        scraper.me_prices_from_category(category_id=cat_id, save_results=True)
        time.sleep(5)
        q = (update(m.MECategories).where(m.MECategories.id == cat_id)).values(last_check=datetime.now())
        session.execute(q)


if __name__ == '__main__':
    check_manager()
