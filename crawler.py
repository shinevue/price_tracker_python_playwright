import os

import sheets
import utils
from const import ME
from scraper import PlayScraper


def me_crawl_for_urls(site=ME):
    ps = PlayScraper(url=site.DOMAIN, render_javascript=True)
    ps.run()
    categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['category_list'])
    inner_categories = []
    for category in categories:
        ps = PlayScraper(url=site.DOMAIN+category, render_javascript=True)
        ps.run()
        inner_categories = ps.content.parse_categories(xpath_selector=site.XPathSelectors['inner_categories'])
        print(inner_categories)

    for inner_cat in inner_categories:
        ps = PlayScraper(url=site.DOMAIN + inner_cat, render_javascript=True)
        ps.run()

