from src.base.page_base import CategoryPage, ProductPage
from src.base.product_base import Product
from src.exceptions import UnmatchingPrices
from src.me.selectors_me import DomainDataME

from src import utils

class MECategoryPage(CategoryPage):
    def extract_products_urls(self):
        pass

    def extract_product_prices(self):
        pass

class MEProductPage(ProductPage):
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
