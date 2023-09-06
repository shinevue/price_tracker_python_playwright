from datetime import datetime

from sqlalchemy.orm import Session

from const import ME
from database import db, models
from scraper import PlayScraper


def me_crawl_for_categories(site=ME,
                            session: Session = db.session):
    ps = PlayScraper(url=site.DOMAIN, render_javascript=True)
    ps.run()
    categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['category_list'])
    inner_categories = []
    for category in categories:
        print('category: ', category)
        ps = PlayScraper(url=site.DOMAIN+category, render_javascript=True)
        ps.run()
        inner_categories.extend(ps.content.parse_categories(xpath_selector=site.XPathSelectors['inner_categories']))
    for cat in inner_categories:
        print(cat)
        session.add(models.MECategories(category_path=cat,
                                        time_discovered=datetime.now()))
    session.commit()

    # for inner_cat in inner_categories:
    #     ps = PlayScraper(url=site.DOMAIN + inner_cat, render_javascript=True)
    #     ps.run()


