from src.base.page_base import CategoryPage, ProductPage
from src.base.product_base import Product


class MECategoryPage(CategoryPage):
    def extract_products_urls(self):
        pass

    def extract_product_prices(self):
        pass

class MEProductPage(ProductPage):
    def extract_product_data(self) -> Product:
        product_item = Product()
        return product_item
