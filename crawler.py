from datetime import datetime

from sqlalchemy.orm import Session

from const import ME
from database import db, models
from scraper import PlayScraper


def me_crawl_for_categories(site=ME,
                            session: Session = db.session):
    # TODO Zmienić sposób szukania lub filtrowania kategorii - niektórych brakuje, niektóre są błędne (nie są końcowymi kategoriami).
    #  Scrapować sitemapę!!!
    # https://www.mediaexpert.pl/sitemap/sitemap.product_categories.xml
    ps = PlayScraper(url=site.DOMAIN, render_javascript=True)
    ps.run()
    categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['category_list'])
    inner_categories = []
    for category in categories:
        print('category: ', category)
        ps = PlayScraper(url=site.DOMAIN+category, render_javascript=True)
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


def me_crawl_category_for_products(site=ME):
    ps = PlayScraper(url=site.DOMAIN+'/telewizory-i-rtv/kina-domowe/subwoofery')
    ps.run()
    products_paths = ps.content.parse_products_from_category(site)
    return products_paths
