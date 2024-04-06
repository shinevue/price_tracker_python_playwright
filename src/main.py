from functools import wraps
import browser
from src.base.product_base import Product
from src.base.extractor_base import PageContent
from src.me.extractor_me import MECategoryExtractor, MEProductExtractor


urls = ["https://en.wikipedia.org/wiki/Security_orchestration",
        "https://en.wikipedia.org/wiki/Security_information_and_event_management",
        "https://en.wikipedia.org/wiki/Security_architecture",
        "https://en.wikipedia.org/wiki/Python",
        ]


def product_page_scrape(urls: list):
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
        product: Product = MEProductExtractor(page_content=page).extract_product_data()
        print(product)
        print(product.name)
        print(product.price)
        print("-"*16)


def category_page_scrape(urls: list):
    b = browser.Browser(render_javascript=True)
    for url in urls:
        print(f"Visiting category page - {url}")

        page: PageContent | None = b.visit_url(url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            continue

        print("visited url: ", page.url)
        print("status code: ", page.status_code)
        print("test fragment of html_tree: ", page.html_tree[:150])

        result = MECategoryExtractor(page_content=page).extract_category_page()
        for item in result:
            if item:
                print(item.url)
                print(item.name)
                print(item.product_code)
                print(item.price)


def managed_scrape():
    pass


if __name__ == "__main__":
    product_page_scrape(urls=["https://www.mediaexpert.pl/gaming/playstation-5/konsole-ps5/konsola-sony-playstation-5-slim"])
    category_page_scrape(urls=["https://www.mediaexpert.pl/agd-do-zabudowy/akcesoria-do-zabudowy/filtry-do-okapow-do-zabudowy"])
