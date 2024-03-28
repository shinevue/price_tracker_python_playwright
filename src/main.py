from functools import wraps
import browser
from src.base.product_base import Product
from src.base.scraper_base import PageContent
from src.me.scraper_me import MEProductScraper


urls = ["https://en.wikipedia.org/wiki/Security_orchestration",
        "https://en.wikipedia.org/wiki/Security_information_and_event_management",
        "https://en.wikipedia.org/wiki/Security_architecture",
        "https://en.wikipedia.org/wiki/Python",
        ]



def product_scrape_single_url(urls: list):
    b = browser.Browser()
    for url in urls:
        print(f"Visiting page - {url}")
        page: PageContent | None = b.visit_url(url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            continue
        print("visited url: ", page.url)
        print("status code: ", page.status_code)
        print("test fragment of html_tree: ", page.html_tree[:150])

        print("Running Product Scraper")
        product: Product = MEProductScraper(page_content=page).extract_product_data()
        print(product)
        print(product.name)
        print(product.price)
        print("-"*16)



if __name__ == "__main__":
    product_scrape_single_url(urls=["https://www.mediaexpert.pl/gaming/playstation-5/konsole-ps5/konsola-sony-playstation-5-slim"])
