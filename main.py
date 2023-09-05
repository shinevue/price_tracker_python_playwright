import os

import utils
import sheets
from dotenv import load_dotenv
from pw_scraper import PlayScraper

load_dotenv()
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = "A2:E2"
URL_LIMIT = 4

if __name__ == '__main__':
    urls = utils.read_urls('urls.txt')
    for url in urls[:URL_LIMIT]:
        my_url = PlayScraper(url=url, render_javascript=True, check_type='default')
        my_url.run()

        creds = sheets.authorize_google()
        if creds:
            sheets.append_to_sheets(creds=creds,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    range_name=RANGE_NAME,
                                    value_input_option="USER_ENTERED",
                                    values=[my_url.content.format_for_sheets()]
                                    )
