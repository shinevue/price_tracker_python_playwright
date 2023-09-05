import os

import sheets
import utils
from const import ME
from scraper import PlayScraper


def me_crawl(site=ME):
    ps = PlayScraper(url=site.DOMAIN, render_javascript=True)
    ps.run()
    categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['category_list'])
    for category in categories:
        ps = PlayScraper(url=site.DOMAIN+category, render_javascript=True)
        ps.run()
