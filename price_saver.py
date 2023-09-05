import os

import sheets
import utils
from const import ME
from scraper import PlayScraper

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"
URL_LIMIT = 4


def scrape():
    urls = utils.read_urls('urls.txt')
    for url in urls[:URL_LIMIT]:
        my_url = PlayScraper(url=url, render_javascript=True)
        my_url.run()
        my_url.content.parse_product_data(site=ME)

        creds = sheets.authorize_google()
        if creds:
            sheets.append_to_sheets(creds=creds,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    range_name=RANGE_NAME,
                                    value_input_option="USER_ENTERED",
                                    values=[my_url.content.format_for_sheets()])
