from src.base.scraper_base import CategoryScraper, ProductScraper
from src.base.product_base import Product
from src.exceptions import UnmatchingPrices
from src.me.selectors_me import DomainDataME

from src import utils


class MECategoryScraper(CategoryScraper):
    def extract_products_urls(self) -> list[str | None]:
        pass

    def extract_products_data(self) -> list[Product | None]:
        pass

class MEProductScraper(ProductScraper):
    def extract_product_data(self) -> Product:
        product_item = Product()
        product_item.name = self.page_content.html_tree.xpath(DomainDataME.XPathSelectors['product_name'])[0]
        prices_found = self.page_content.html_tree.xpath(DomainDataME.XPathSelectors['main_price'])
        if prices_found:
            if utils.compare_list_elements(prices_found):
                product_item.price = float(prices_found[0][:-2] + '.' + prices_found[0][-2:])
            else:
                print('prices_found: ', prices_found)
                raise UnmatchingPrices
        return product_item
