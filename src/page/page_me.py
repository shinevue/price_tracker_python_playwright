from src.page.page_base import CategoryPage, ProductPage


class MECategoryPage(CategoryPage):
    def extract_products_urls(self):
        pass

    def extract_product_prices(self):
        pass

class MEProductPage(ProductPage):
    def extract_product_data(self):
        pass
