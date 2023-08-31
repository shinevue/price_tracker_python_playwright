import os

import utils
import sheets
from dotenv import load_dotenv
from pw_scraper import PlayScraper

load_dotenv()
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
URL_LIMIT = 4

if __name__ == '__main__':
    urls = utils.read_urls('urls.txt')
    for url in urls[:URL_LIMIT]:
        my_url = PlayScraper(url=url, render_javascript=True)
        my_url.run()
        print('found name: ', my_url.content.product_name)
        print('found_price: ', my_url.content.price)

        creds = sheets.authorize_google()
        if creds:
            range_name = "A2:E2"
            values = [my_url.content.for_sheets()]

            sheets.append_to_sheets(creds=creds,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    range_name=range_name,
                                    value_input_option="USER_ENTERED",
                                    values=values
                                    )
        # print(etree.tostring(my_url.content.html_tree, pretty_print=True))
