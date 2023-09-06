import os

from database import sheets
import utils
from const import ME
from scraper import PlayScraper

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"
URL_LIMIT = 50


def me_scrape_price(paths_list: list[str] = None):
    if not paths_list:
        try:
            paths_list = utils.read_urls('urls.txt')
        except:
            pass

    for path in paths_list[:URL_LIMIT]:
        my_url = PlayScraper(url=ME.DOMAIN + path, render_javascript=True)
        my_url.run()
        my_url.content.parse_product_data(site=ME)

        creds = sheets.authorize_google()
        if creds:
            sheets.append_to_sheets(creds=creds,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    range_name=RANGE_NAME,
                                    value_input_option="USER_ENTERED",
                                    values=[my_url.content.format_for_sheets()])
